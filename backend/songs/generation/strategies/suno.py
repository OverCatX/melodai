from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from django.conf import settings

from ..base import SongGenerationStrategy
from ..types import SongGenerationRequest, SongGenerationResult


class SunoSongGeneratorStrategy(SongGenerationStrategy):
    """
    Integrates with Suno API (api.sunoapi.org): create task + poll record-info.
    Auth: Authorization: Bearer <token> on every request.
    """

    GENERATE_PATH = "/api/v1/generate"
    RECORD_INFO_PATH = "/api/v1/generate/record-info"

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        callback_url: Optional[str] = None,
        timeout_seconds: float = 60.0,
    ):
        if not api_key:
            raise ValueError(
                "SunoSongGeneratorStrategy requires SUNO_API_KEY when GENERATOR_STRATEGY=suno"
            )
        self._api_key = api_key
        self._base = (base_url or getattr(settings, "SUNO_API_BASE_URL", "")).rstrip("/")
        self._model = model or getattr(settings, "SUNO_MODEL", "V4_5ALL")
        self._callback_url = callback_url or getattr(
            settings, "SUNO_CALLBACK_URL", "https://example.com/suno-callback-placeholder"
        )
        self._timeout = timeout_seconds

    def _headers(self, *, json_body: bool = False) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def generate(self, request: SongGenerationRequest) -> SongGenerationResult:
        prompt = request.prompt_text.strip()
        if len(prompt) > 500:
            prompt = prompt[:500]

        body = {
            "customMode": False,
            "instrumental": False,
            "prompt": prompt,
            "callBackUrl": self._callback_url,
            "model": self._model,
        }
        url = f"{self._base}{self.GENERATE_PATH}"
        try:
            resp = requests.post(
                url,
                json=body,
                headers=self._headers(json_body=True),
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            return SongGenerationResult(
                success=False,
                completed=False,
                error_message=f"Suno request failed: {exc}",
            )

        try:
            payload: Dict[str, Any] = resp.json()
        except ValueError:
            return SongGenerationResult(
                success=False,
                completed=False,
                error_message=f"Suno invalid JSON (HTTP {resp.status_code})",
            )

        code = payload.get("code")
        if code != 200:
            msg = payload.get("msg") or resp.text
            return SongGenerationResult(
                success=False,
                completed=False,
                error_message=f"Suno generate error {code}: {msg}",
            )

        data = payload.get("data") or {}
        task_id = data.get("taskId")
        if not task_id:
            return SongGenerationResult(
                success=False,
                completed=False,
                error_message="Suno response missing data.taskId",
            )

        return SongGenerationResult(
            success=True,
            completed=False,
            external_task_id=str(task_id),
            external_status="PENDING",
        )

    def fetch_status(self, external_task_id: str) -> SongGenerationResult:
        url = f"{self._base}{self.RECORD_INFO_PATH}"
        params = {"taskId": external_task_id}
        try:
            resp = requests.get(
                url, params=params, headers=self._headers(), timeout=self._timeout
            )
        except requests.RequestException as exc:
            return SongGenerationResult(
                success=False,
                completed=False,
                external_task_id=external_task_id,
                error_message=f"Suno record-info failed: {exc}",
            )

        try:
            payload: Dict[str, Any] = resp.json()
        except ValueError:
            return SongGenerationResult(
                success=False,
                completed=False,
                external_task_id=external_task_id,
                error_message=f"Suno invalid JSON (HTTP {resp.status_code})",
            )

        code = payload.get("code")
        if code != 200:
            msg = payload.get("msg") or resp.text
            return SongGenerationResult(
                success=False,
                completed=False,
                external_task_id=external_task_id,
                error_message=f"Suno record-info error {code}: {msg}",
            )

        data = payload.get("data") or {}
        status = data.get("status")
        err_msg = data.get("errorMessage")

        audio_url = _first_audio_url(data)

        terminal_fail = status in (
            "CREATE_TASK_FAILED",
            "GENERATE_AUDIO_FAILED",
            "CALLBACK_EXCEPTION",
            "SENSITIVE_WORD_ERROR",
        )
        if terminal_fail:
            return SongGenerationResult(
                success=False,
                completed=True,
                external_task_id=external_task_id,
                external_status=status,
                error_message=err_msg or status,
            )

        if status == "SUCCESS":
            return SongGenerationResult(
                success=True,
                completed=True,
                external_task_id=external_task_id,
                external_status=status,
                audio_url=audio_url,
            )

        return SongGenerationResult(
            success=True,
            completed=False,
            external_task_id=external_task_id,
            external_status=status,
            audio_url=audio_url,
        )


def _first_audio_url(data: Dict[str, Any]) -> Optional[str]:
    response = data.get("response") or {}
    suno_data = response.get("sunoData")
    if isinstance(suno_data, list) and suno_data:
        first = suno_data[0]
        if isinstance(first, dict):
            return first.get("audioUrl") or first.get("audio_url")
    return None
