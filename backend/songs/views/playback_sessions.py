from rest_framework import viewsets

from ..models import PlaybackSession
from ..serializers import PlaybackSessionSerializer


class PlaybackSessionViewSet(viewsets.ModelViewSet):
    """
    CRUD for PlaybackSession.
    list   GET    /api/playback-sessions/
    create POST   /api/playback-sessions/
    read   GET    /api/playback-sessions/{id}/
    update PUT    /api/playback-sessions/{id}/
    patch  PATCH  /api/playback-sessions/{id}/
    delete DELETE /api/playback-sessions/{id}/
    """

    queryset = PlaybackSession.objects.all()
    serializer_class = PlaybackSessionSerializer
