from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..serializers import UserSerializer
from ..utils_auth import get_or_create_google_user, issue_session_token


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_config(request):
    """
    GET /api/auth/config/
    Public: OAuth web client id for Google Sign-In (not a secret; used by the JS client).
    Lets the frontend show the Google button when only backend/.env is configured.
    """
    return Response(
        {
            "google_client_id": (
                getattr(settings, "GOOGLE_OAUTH_CLIENT_ID", None) or ""
            ).strip()
        }
    )


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
