import uuid
from django.db import models

from .song import Song


class SharedSong(models.Model):
    """
    Produced when a Song is shared (Song produces 0..1 SharedSong).
    accessibleByGuest controls whether non-registered users can access the link.
    """

    share_id            = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    song                = models.OneToOneField(Song, on_delete=models.CASCADE, related_name="shared_song")
    share_link          = models.URLField(unique=True)
    shared_at           = models.DateTimeField(auto_now_add=True)
    accessible_by_guest = models.BooleanField(default=False)

    def __str__(self):
        return f"Shared: {self.song.title}"
