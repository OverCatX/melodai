from __future__ import annotations

import uuid
from dataclasses import dataclass


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
