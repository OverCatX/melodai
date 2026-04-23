import uuid
from django.db import models

from .song import Song


class Draft(models.Model):
    """
    A Song can be saved as one or more Drafts (0..* in the domain model).
    retentionPolicy determines how long a draft is kept before auto-deletion.
    """

    draft_id         = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    song             = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="drafts")
    saved_at         = models.DateTimeField(auto_now_add=True)
    is_submitted     = models.BooleanField(default=False)
    retention_policy = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-saved_at"]

    def __str__(self):
        return f"Draft of '{self.song.title}' at {self.saved_at:%Y-%m-%d %H:%M}"
