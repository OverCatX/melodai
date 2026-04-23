from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import uuid


@dataclass(frozen=True)
class SongGenerationRequest:
    """
    Input to a song generation strategy (prompt/title/style context).
    `internal_request_uuid` ties results to our AIGenerationRequest row.
    """

    internal_request_uuid: uuid.UUID
    title: str
    prompt_text: str
    style_hint: str


@dataclass(frozen=True)
class SongGenerationResult:
    """Output from generate() or status polling (task id, URLs, status)."""

    success: bool
    completed: bool
    external_task_id: Optional[str] = None
    external_status: Optional[str] = None
    audio_url: Optional[str] = None
    error_message: Optional[str] = None
