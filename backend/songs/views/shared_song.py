from rest_framework import viewsets

from ..models import SharedSong
from ..serializers import SharedSongSerializer


class SharedSongViewSet(viewsets.ModelViewSet):
    """
    CRUD for SharedSong.
    list   GET    /api/shared-songs/
    create POST   /api/shared-songs/
    read   GET    /api/shared-songs/{id}/
    update PUT    /api/shared-songs/{id}/
    patch  PATCH  /api/shared-songs/{id}/
    delete DELETE /api/shared-songs/{id}/
    """

    queryset = SharedSong.objects.select_related("song").all()
    serializer_class = SharedSongSerializer
