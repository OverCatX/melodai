import uuid
from django.db import models


class PlaybackSession(models.Model):
    """
    Represents an active or paused playback state for a song.
    loopStart and loopEnd are optional ([0..1] in the domain model).
    """

    session_id         = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    current_position   = models.FloatField(default=0.0, help_text="Playback position in seconds")
    loop_start         = models.FloatField(null=True, blank=True, help_text="Loop start in seconds")
    loop_end           = models.FloatField(null=True, blank=True, help_text="Loop end in seconds")
    equalizer_settings = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"Session {self.session_id}"
