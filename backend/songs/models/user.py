import uuid
from django.db import models


class User(models.Model):
    """
    A registered user of the platform.
    Authentication (Google OAuth) is outside scope for this exercise;
    the fields below reflect the domain model attributes exactly.
    """

    user_id       = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    google_id     = models.CharField(max_length=255, unique=True)
    email         = models.EmailField(unique=True)
    display_name  = models.CharField(max_length=255)
    session_token = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self):
        return self.display_name
