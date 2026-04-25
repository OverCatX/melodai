from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SongGenerationResult:
    """Output from generate() or status polling (task id, URLs, status)."""

    success: bool
    completed: bool
    external_task_id: Optional[str] = None
    external_status: Optional[str] = None
    audio_url: Optional[str] = None
    error_message: Optional[str] = None
