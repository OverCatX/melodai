from rest_framework import viewsets

from ..models import SongPrompt
from ..serializers import SongPromptSerializer


class SongPromptViewSet(viewsets.ModelViewSet):
    """
    CRUD for SongPrompt.
    list   GET    /api/song-prompts/
    create POST   /api/song-prompts/
    read   GET    /api/song-prompts/{id}/
    update PUT    /api/song-prompts/{id}/
    patch  PATCH  /api/song-prompts/{id}/
    delete DELETE /api/song-prompts/{id}/
    """

    queryset = SongPrompt.objects.select_related("song").all()
    serializer_class = SongPromptSerializer
