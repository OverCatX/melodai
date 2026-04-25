import uuid

from django.db import models


class User(models.Model):
    """
    A user of the platform. Identified by unique username, or by Google `google_id` for OAuth.
    `session_token` is issued on login (username flow or Google) for Bearer API auth.
    """

    user_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    username = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True, default="")
    google_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True, db_index=True
    )
    session_token = models.CharField(
        max_length=128, blank=True, null=True, unique=True, db_index=True
    )

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self) -> bool:
        """Allow DRF to treat API users as authenticated when resolved from Bearer token."""
        return self.pk is not None

    @property
    def is_anonymous(self) -> bool:
        return False
