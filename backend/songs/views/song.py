import re

import requests
from django.core.exceptions import ImproperlyConfigured
from django.http import StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from ..generation.service import refresh_generation_status
from ..models import AIGenerationRequest, Song, SongPrompt, User
from ..serializers import DraftSerializer, SongPromptSerializer, SongSerializer

_FILENAME_SAFE = re.compile(r"[^\w\s\-._]", re.UNICODE)


def _safe_download_basename(name: str) -> str:
    s = _FILENAME_SAFE.sub("", (name or "").strip())
    s = s.replace(" ", "_") or "song"
    return s[:200]


class SongViewSet(viewsets.ModelViewSet):
    """
    CRUD for Song.
    list   GET    /api/songs/   (empty without ?user_id=; prefer GET /api/users/{id}/songs/)
    create POST   /api/songs/
    read   GET    /api/songs/{id}/?user_id=<owner>  — scoping: only the owning user’s row
    update PUT    /api/songs/{id}/
    patch  PATCH  /api/songs/{id}/
    delete DELETE /api/songs/{id}/
    """

    queryset = Song.objects.select_related("user", "playback_session").all()
    serializer_class = SongSerializer

    def get_queryset(self):
        qs = Song.objects.select_related("user", "playback_session").all()
        if getattr(self, "action", None) == "create":
            return qs
        u = self.request.user
        if isinstance(u, User) and u.is_authenticated:
            raw = self.request.query_params.get("user_id")
            if raw is not None and str(raw).strip() != "":
                try:
                    if int(raw) != u.id:
                        return Song.objects.none()
                except (TypeError, ValueError):
                    return Song.objects.none()
            return qs.filter(user_id=u.id)
        raw = self.request.query_params.get("user_id")
        if raw is not None and str(raw).strip() != "":
            try:
                return qs.filter(user_id=int(raw))
            except (TypeError, ValueError):
                return Song.objects.none()
        return Song.objects.none()

    def perform_create(self, serializer):
        u = self.request.user
        if isinstance(u, User) and u.is_authenticated:
            target = serializer.validated_data.get("user")
            if target is not None and target.id != u.id:
                raise PermissionDenied("Cannot create songs for another user.")
        serializer.save()

    @action(detail=True, methods=["get"], url_path="prompt")
    def prompt(self, request, pk=None):
        """GET /api/songs/{id}/prompt/ — the prompt that defined this song."""
        song = self.get_object()
        try:
            serializer = SongPromptSerializer(song.prompt)
            return Response(serializer.data)
        except SongPrompt.DoesNotExist:
            return Response(
                {"detail": "No prompt attached to this song."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["get"], url_path="drafts")
    def drafts(self, request, pk=None):
        """GET /api/songs/{id}/drafts/ — all saved drafts of this song."""
        song = self.get_object()
        serializer = DraftSerializer(song.drafts.all(), many=True)
        return Response(serializer.data)
    @action(detail=True, methods=["post"], url_path="sync-status")
    def sync_status(self, request, pk=None):
        """POST /api/songs/{id}/sync-status/ — trigger status refresh for the latest generation request."""
        song = self.get_object()
        # Find the latest request for this song
        ai_request = AIGenerationRequest.objects.filter(prompt__song=song).order_by("-id").first()
        if not ai_request:
            return Response({"detail": "No generation request found for this song."}, status=status.HTTP_404_NOT_FOUND)
        
        if ai_request.status == "COMPLETED":
            return Response(self.get_serializer(song).data)

        try:
            refresh_generation_status(ai_request)
        except ImproperlyConfigured as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            # Already completed or no external id
            pass
            
        song.refresh_from_db()
        return Response(self.get_serializer(song).data)

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        """
        GET /api/songs/{id}/download/ — stream audio from audio_file_url (Suno CDN) so the browser can save a file.
        """
        song = self.get_object()
        src = (song.audio_file_url or "").strip()
        if not src:
            return Response(
                {"detail": "No audio file is available for this song yet."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            upstream = requests.get(src, stream=True, timeout=120)
        except requests.RequestException as exc:
            return Response(
                {"detail": f"Could not fetch audio: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        if upstream.status_code != 200:
            upstream.close()
            return Response(
                {"detail": f"Audio source returned HTTP {upstream.status_code}."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        content_type = upstream.headers.get("Content-Type", "audio/mpeg")
        ext = ".mp3"
        if "wav" in content_type.lower():
            ext = ".wav"
        elif "flac" in content_type.lower():
            ext = ".flac"
        elif "ogg" in content_type.lower() or "opus" in content_type.lower():
            ext = ".ogg"
        base = _safe_download_basename(song.title)
        filename = f"{base}{ext}"

        def stream():
            try:
                for chunk in upstream.iter_content(chunk_size=64 * 1024):
                    if chunk:
                        yield chunk
            finally:
                upstream.close()

        resp = StreamingHttpResponse(
            stream(),
            content_type=content_type,
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        if cl := upstream.headers.get("Content-Length"):
            resp["Content-Length"] = cl
        return resp
