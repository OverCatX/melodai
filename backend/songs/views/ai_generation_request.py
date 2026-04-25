import time
from typing import Iterator

from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from django.http import StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from ..generation.service import refresh_generation_status, run_generation
from ..models import AIGenerationRequest, GenerationStatus
from ..serializers import AIGenerationRequestSerializer

# Match frontend Generate.tsx polling (Suno)
_STREAM_POLL_MAX = 60
_STREAM_POLL_INTERVAL_SEC = 5.0


class AIGenerationRequestViewSet(viewsets.ModelViewSet):
    """
    CRUD for AIGenerationRequest.
    list   GET    /api/generation-requests/
    create POST   /api/generation-requests/
    read   GET    /api/generation-requests/{id}/
    update PUT    /api/generation-requests/{id}/
    patch  PATCH  /api/generation-requests/{id}/
    delete DELETE /api/generation-requests/{id}/

    Strategy pattern (Exercise 4):
    run   POST   /api/generation-requests/{id}/run/   — start generation (mock or Suno)
          Optional ?stream=1 — text/plain progress + final JSON line (curl -N for Suno)
    poll  POST   /api/generation-requests/{id}/poll/ — poll Suno task status (record-info)
    """

    queryset = AIGenerationRequest.objects.select_related("prompt", "prompt__song").all()
    serializer_class = AIGenerationRequestSerializer

    def _conflict_response(self, instance):
        return Response(
            {
                "detail": "A generation request already exists for this prompt.",
                "code": "duplicate_prompt",
                "resource": self.get_serializer(instance).data,
            },
            status=status.HTTP_409_CONFLICT,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prompt = serializer.validated_data["prompt"]
        existing = AIGenerationRequest.objects.filter(prompt_id=prompt.pk).first()
        if existing:
            return self._conflict_response(existing)
        try:
            with transaction.atomic():
                self.perform_create(serializer)
        except IntegrityError:
            existing = AIGenerationRequest.objects.filter(prompt_id=prompt.pk).first()
            if existing:
                return self._conflict_response(existing)
            raise
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _run_json(self, ai_request: AIGenerationRequest) -> Response:
        try:
            run_generation(ai_request)
        except ImproperlyConfigured as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        ai_request.refresh_from_db()
        serializer = self.get_serializer(ai_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _render_request_json(self, ai_request: AIGenerationRequest) -> str:
        ai_request.refresh_from_db()
        data = self.get_serializer(ai_request).data
        return JSONRenderer().render(data).decode("utf-8")

    def _run_streaming(self, ai_request: AIGenerationRequest) -> StreamingHttpResponse:
        """
        text/plain: [stream]/[poll] lines, then one final JSON line (same as normal 200);
        use curl -N so lines show as they arrive. Last line: parse with `tail -1 | jq .`
        """

        def chunks() -> Iterator[bytes]:
            def line(s: str) -> bytes:
                return (s if s.endswith("\n") else s + "\n").encode("utf-8")

            yield line(f"[stream] generation_request_id={ai_request.id} — running…")
            try:
                run_generation(ai_request)
            except ImproperlyConfigured as exc:
                err = {"detail": str(exc), "_stream": "error"}
                yield line(JSONRenderer().render(err).decode("utf-8"))
                return
            except ValueError as exc:
                err = {"detail": str(exc), "_stream": "error"}
                yield line(JSONRenderer().render(err).decode("utf-8"))
                return

            ai_request.refresh_from_db()
            st = ai_request.status
            ext = ai_request.external_status or "—"
            if st == GenerationStatus.COMPLETED:
                yield line(
                    f"[stream] done  status={st}  external={ext}  (no async polling needed)"
                )
                yield line(self._render_request_json(ai_request))
                return
            if st == GenerationStatus.FAILED:
                yield line(
                    f"[stream] run ended with failure  status={st}  external={ext}"
                )
                yield line(self._render_request_json(ai_request))
                return
            if st != GenerationStatus.IN_PROGRESS:
                yield line(f"[stream] unexpected status={st}  external={ext}")
                yield line(self._render_request_json(ai_request))
                return

            yield line(
                f"[stream] task created — polling every "
                f"{_STREAM_POLL_INTERVAL_SEC:g}s (max {_STREAM_POLL_MAX} attempts)…  "
                f"task={ai_request.external_task_id!r}"
            )
            for n in range(1, _STREAM_POLL_MAX + 1):
                time.sleep(_STREAM_POLL_INTERVAL_SEC)
                try:
                    refresh_generation_status(ai_request)
                except ImproperlyConfigured as exc:
                    err = {"detail": str(exc), "_stream": "error"}
                    yield line(JSONRenderer().render(err).decode("utf-8"))
                    return
                except ValueError as exc:
                    err = {"detail": str(exc), "_stream": "error"}
                    yield line(JSONRenderer().render(err).decode("utf-8"))
                    return
                ai_request.refresh_from_db()
                st2 = ai_request.status
                ext2 = ai_request.external_status or "—"
                yield line(
                    f"[poll] {n}/{_STREAM_POLL_MAX}  status={st2}  external={ext2}"
                )
                if st2 in (GenerationStatus.COMPLETED, GenerationStatus.FAILED):
                    yield line(
                        f"[stream] done after {n} poll(s)  status={st2}  external={ext2}"
                    )
                    yield line(self._render_request_json(ai_request))
                    return

            yield line(
                f"[stream] still IN_PROGRESS after {_STREAM_POLL_MAX} polls — "
                "use POST …/poll/ or the UI, or run again with ?stream=1"
            )
            yield line(self._render_request_json(ai_request))

        resp = StreamingHttpResponse(
            chunks(),
            content_type="text/plain; charset=utf-8",
        )
        resp["X-Accel-Buffering"] = "no"
        return resp

    @action(detail=True, methods=["post"], url_path="run")
    def run(self, request, pk=None):
        """
        POST /api/generation-requests/{id}/run/ — execute configured generator strategy.

        Query: stream=1|true — stream progress to the client (use curl -N) while Suno
        runs; the last line is JSON (same as non-stream 200). Mock finishes in one step.
        """
        ai_request = self.get_object()
        stream = request.query_params.get("stream", "").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        if stream:
            return self._run_streaming(ai_request)
        return self._run_json(ai_request)

    @action(detail=True, methods=["post"], url_path="poll")
    def poll(self, request, pk=None):
        """POST /api/generation-requests/{id}/poll/ — refresh status (Suno record-info)."""
        ai_request = self.get_object()
        try:
            refresh_generation_status(ai_request)
        except ImproperlyConfigured as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        ai_request.refresh_from_db()
        serializer = self.get_serializer(ai_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
