from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import User


class BearerSessionAuthentication(BaseAuthentication):
    """
    Authorization: Bearer <session_token> — matches User.session_token.
    """

    def authenticate(self, request):
        auth = request.headers.get("Authorization") or ""
        if not auth.startswith("Bearer "):
            return None
        token = auth[7:].strip()
        if not token:
            return None
        try:
            user = User.objects.get(session_token=token)
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("Invalid session token.") from exc
        return (user, None)
