from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Song, SongPrompt
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
