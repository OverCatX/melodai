import secrets

from django.utils.text import slugify

from .models import User


def issue_session_token(user: User) -> str:
    token = secrets.token_urlsafe(32)
    user.session_token = token
    user.save(update_fields=["session_token"])
    return token


def unique_username_for_google(email: str, sub: str) -> str:
    if email and "@" in email:
        base = email.split("@", 1)[0]
    else:
        base = f"google_{sub[:12]}"
    s = (slugify(base) or f"g{sub[:16]}")[:200]
    if not s:
        s = f"g{sub[:16]}"
    if not User.objects.filter(username=s).exists():
        return s
    n = 1
    while True:
        candidate = f"{s}_{n}"
        if len(candidate) > 255:
            candidate = f"{s[:240]}_{n}"
        if not User.objects.filter(username=candidate).exists():
            return candidate
        n += 1


def get_or_create_google_user(sub: str, email: str, display_name: str) -> User:
    user, created = User.objects.get_or_create(
        google_id=sub,
        defaults={
            "username": unique_username_for_google(email, sub),
            "display_name": (display_name or email or "User")[:255],
            "email": email,
        },
    )
    changed = []
    if email and user.email != email:
        user.email = email
        changed.append("email")
    if display_name and (
        not user.display_name or user.display_name == user.username
    ):
        user.display_name = display_name[:255]
        changed.append("display_name")
    if changed:
        user.save(update_fields=changed)
    return user
