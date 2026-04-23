import uuid
from django.db import models

from .enums import Occasion, MoodTone, SingerTone
from .song import Song


class SongPrompt(models.Model):
    """
    Captures the creative input that defines a Song.
    Exactly one SongPrompt maps to exactly one Song (1..1 both ways).
    """

    prompt_id     = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    song          = models.OneToOneField(Song, on_delete=models.CASCADE, related_name="prompt")
    title         = models.CharField(max_length=255)
    occasion      = models.CharField(max_length=20, choices=Occasion.choices)
    mood_and_tone = models.CharField(max_length=20, choices=MoodTone.choices)
    singer_tone   = models.CharField(max_length=20, choices=SingerTone.choices)
    description   = models.TextField(blank=True)

    def __str__(self):
        return f"Prompt: {self.title} ({self.get_occasion_display()})"
