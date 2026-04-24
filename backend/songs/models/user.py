import uuid
from django.db import models


class User(models.Model):
    """
    A user of the platform. Identified by a unique username.
    No external auth required — username is the only required field.
    """

    user_id      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    username     = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username
