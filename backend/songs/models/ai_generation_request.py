import uuid
from django.db import models

from .enums import GenerationStatus
from .song_prompt import SongPrompt


class AIGenerationRequest(models.Model):
    """
    Created when a SongPrompt triggers the AI generation pipeline.
    Exactly one request per prompt (1..1).
    errorMessage is optional ([0..1] in the domain model).
    """

    request_id    = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    prompt        = models.OneToOneField(
        SongPrompt, on_delete=models.CASCADE, related_name="generation_request"
    )
    submitted_at  = models.DateTimeField(auto_now_add=True)
    status        = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.IN_PROGRESS,
    )
    error_message = models.TextField(blank=True)  # optional [0..1]
    # External provider (e.g. Suno task id + API status); blank when using mock-only runs
    external_task_id = models.CharField(max_length=128, blank=True, db_index=True)
    external_status = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"Request {self.request_id} – {self.get_status_display()}"
