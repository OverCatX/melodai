from __future__ import annotations

import hashlib

from ..base import SongGenerationStrategy
from ..song_generation_request import SongGenerationRequest
from ..song_generation_result import SongGenerationResult


MOCK_AUDIO_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/audio/dummy-audio.mp3"


class MockSongGeneratorStrategy(SongGenerationStrategy):
    """
    Offline, deterministic generator: no network calls.
    Produces a stable fake task id and a well-known placeholder audio URL.
    """

    def generate(self, request: SongGenerationRequest) -> SongGenerationResult:
        digest = hashlib.sha256(
            f"{request.internal_request_uuid}:{request.title}:{request.prompt_text}".encode()
        ).hexdigest()[:16]
        task_id = f"mock-{digest}"
        return SongGenerationResult(
            success=True,
            completed=True,
            external_task_id=task_id,
            external_status="SUCCESS",
            audio_url=MOCK_AUDIO_URL,
        )

    def fetch_status(self, external_task_id: str) -> SongGenerationResult:
        return SongGenerationResult(
            success=True,
            completed=True,
            external_task_id=external_task_id,
            external_status="SUCCESS",
            audio_url=MOCK_AUDIO_URL,
        )
