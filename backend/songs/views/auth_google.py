import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers import UserSerializer
from ..utils_auth import get_or_create_google_user, issue_session_token

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"


def _frontend_base() -> str:
    return (
        getattr(settings, "GOOGLE_OAUTH_FRONTEND_BASE", None) or "http://localhost:5173"
    ).strip().rstrip("/")


def _redirect_frontend_error(code: str, message: str = "") -> HttpResponseRedirect:
    q = urlencode({"error": code, "detail": (message or "")[:300]})
    return HttpResponseRedirect(f"{_frontend_base()}/auth/callback?{q}")


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_config(request):
    """
    GET /api/auth/config/
    Public: client id, full URL to start browser OAuth, and whether callback env is complete.
    """
    client_id = (getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", None) or "").strip()
    client_secret = (getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", None) or "").strip()
    login_path = "/api/auth/google/login/"
    login_url = request.build_absolute_uri(login_path) if client_id else ""
    ready = bool(client_id and client_secret)
    return Response(
        {
            "google_client_id": client_id,
            "google_login_url": login_url,
            "google_oauth_ready": ready,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_google_login(request):
    """
    GET /api/auth/google/login/
    Redirects the browser to Google's OAuth consent screen (authorization code flow).
    """
    client_id = (getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", None) or "").strip()
    client_secret = (getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", None) or "").strip()
    redirect_uri = (getattr(settings, "GOOGLE_OAUTH_REDIRECT_URI", None) or "").strip()

    if not client_id or not client_secret or not redirect_uri:
        return _redirect_frontend_error(
            "oauth_not_configured",
            "Set GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, and "
            "GOOGLE_OAUTH_REDIRECT_URI in backend/.env.",
        )

    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    request.session["google_oauth_frontend_base"] = _frontend_base()

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    url = f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"
    return HttpResponseRedirect(url)


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_google_callback(request):
    """
    GET /api/auth/google/callback/
    OAuth redirect target: exchange ?code= for tokens, verify id_token, issue app session,
    redirect to the SPA /auth/callback with user fields in the query string.
    """
    frontend_base_raw = request.session.pop(
        "google_oauth_frontend_base", None
    ) or _frontend_base()
    frontend_base = str(frontend_base_raw).strip().rstrip("/")

    if request.GET.get("error"):
        err = request.GET.get("error", "access_denied")
        desc = request.GET.get("error_description", "")
        request.session.pop("google_oauth_state", None)
        q = urlencode({"error": err, "detail": (desc or "")[:300]})
        return HttpResponseRedirect(f"{frontend_base}/auth/callback?{q}")

    code = (request.GET.get("code") or "").strip()
    state = (request.GET.get("state") or "").strip()
    expected = request.session.get("google_oauth_state")
    if not code or not state or not expected or state != expected:
        request.session.pop("google_oauth_state", None)
        q = urlencode(
            {
                "error": "invalid_state",
                "detail": "Session expired or invalid. Try signing in again.",
            }
        )
        return HttpResponseRedirect(f"{frontend_base}/auth/callback?{q}")

    request.session.pop("google_oauth_state", None)

    client_id = (getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", None) or "").strip()
    client_secret = (getattr(settings, "GOOGLE_OAUTH_CLIENT_SECRET", None) or "").strip()
    redirect_uri = (getattr(settings, "GOOGLE_OAUTH_REDIRECT_URI", None) or "").strip()

    try:
        token_res = requests.post(
            GOOGLE_TOKEN_ENDPOINT,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        if not token_res.ok:
            detail = token_res.text[:300]
            try:
                detail = str(token_res.json().get("error_description", detail))[:300]
            except (TypeError, ValueError):
                pass
            q = urlencode({"error": "token_exchange_failed", "detail": detail})
            return HttpResponseRedirect(f"{frontend_base}/auth/callback?{q}")
        tokens = token_res.json()
    except (requests.RequestException, ValueError) as exc:
        q = urlencode({"error": "token_exchange_failed", "detail": str(exc)[:200]})
        return HttpResponseRedirect(f"{frontend_base}/auth/callback?{q}")

    id_tok = (tokens.get("id_token") or "").strip()
    if not id_tok:
        q = urlencode(
            {
                "error": "no_id_token",
                "detail": "Google did not return an id_token.",
            }
        )
        return HttpResponseRedirect(f"{frontend_base}/auth/callback?{q}")

    try:
        idinfo = id_token.verify_oauth2_token(
            id_tok, google_requests.Request(), client_id
        )
    except ValueError as exc:
        q = urlencode({"error": "invalid_id_token", "detail": str(exc)[:200]})
        return HttpResponseRedirect(f"{frontend_base}/auth/callback?{q}")

    sub = idinfo.get("sub")
    if not sub:
        q = urlencode({"error": "missing_sub", "detail": "Token missing subject."})
        return HttpResponseRedirect(f"{frontend_base}/auth/callback?{q}")

    email = (idinfo.get("email") or "").strip()[:254]
    display_name = (
        idinfo.get("name") or idinfo.get("email") or "User"
    ).strip()[:255]

    user = get_or_create_google_user(sub, email, display_name)
    issue_session_token(user)
    data = UserSerializer(user).data

    params = {
        "session_token": user.session_token or "",
        "id": str(user.id),
        "username": data.get("username") or "",
        "display_name": data.get("display_name") or "",
        "email": data.get("email") or "",
    }
    return HttpResponseRedirect(f"{frontend_base}/auth/callback?{urlencode(params)}")


@api_view(["POST"])
@permission_classes([AllowAny])
def auth_google(request):
    """
    POST /api/auth/google/
    Body: {"id_token": "<JWT from Google Sign-In / JS client>"}
    Returns user fields plus session_token for Bearer API access.
    """
    client_id = (getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", None) or "").strip()
    if not client_id:
        return Response(
            {
                "detail": "Google OAuth is not configured (GOOGLE_OAUTH_CLIENT_ID).",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    id_tok = (request.data.get("id_token") or "").strip()
    if not id_tok:
        return Response(
            {"detail": "id_token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            id_tok, google_requests.Request(), client_id
        )
    except ValueError as exc:
        return Response(
            {"detail": f"Invalid id_token: {exc}"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    sub = idinfo.get("sub")
    if not sub:
        return Response(
            {"detail": "Token missing subject (sub)."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    email = (idinfo.get("email") or "").strip()[:254]
    display_name = (
        idinfo.get("name") or idinfo.get("email") or "User"
    ).strip()[:255]

    user = get_or_create_google_user(sub, email, display_name)
    issue_session_token(user)
    data = UserSerializer(user).data
    data["session_token"] = user.session_token
    return Response(data, status=status.HTTP_200_OK)
