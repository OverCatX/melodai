from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..generation.service import refresh_generation_status
from ..models import AIGenerationRequest, Song, SongPrompt
from ..serializers import DraftSerializer, SongPromptSerializer, SongSerializer


class SongViewSet(viewsets.ModelViewSet):
    """
    CRUD for Song.
    list   GET    /api/songs/
    create POST   /api/songs/
    read   GET    /api/songs/{id}/
    update PUT    /api/songs/{id}/
    patch  PATCH  /api/songs/{id}/
    delete DELETE /api/songs/{id}/
    """

    queryset = Song.objects.select_related("user", "playback_session").all()
    serializer_class = SongSerializer

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
