from __future__ import annotations

from abc import ABC, abstractmethod

from .types import SongGenerationRequest, SongGenerationResult


class SongGenerationStrategy(ABC):
    """
    Strategy interface: interchangeable song generation behavior.
    Implementations must be side-effect free on the database; persistence is
    handled by the application service layer.
    """

    @abstractmethod
    def generate(self, request: SongGenerationRequest) -> SongGenerationResult:
        """Start generation (mock may finish synchronously; Suno returns a task id)."""
        raise NotImplementedError

    def fetch_status(self, external_task_id: str) -> SongGenerationResult:
        """
        Poll remote status for an existing task. Default: not supported.
        Suno implements this via GET /api/v1/generate/record-info.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement fetch_status"
        )
