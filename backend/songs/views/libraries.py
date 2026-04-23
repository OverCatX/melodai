from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Library, Song
from ..serializers import LibrarySerializer


class LibraryViewSet(viewsets.ModelViewSet):
    """
    CRUD for Library.
    list   GET    /api/libraries/
    create POST   /api/libraries/
    read   GET    /api/libraries/{id}/
    update PUT    /api/libraries/{id}/
    patch  PATCH  /api/libraries/{id}/
    delete DELETE /api/libraries/{id}/
    """

    queryset = Library.objects.prefetch_related("songs").select_related("user").all()
    serializer_class = LibrarySerializer

    @action(detail=True, methods=["post"], url_path="add-song")
    def add_song(self, request, pk=None):
        """POST /api/libraries/{id}/add-song/ — add a song to the library."""
        library = self.get_object()
        song_id = request.data.get("song_id")
        if not song_id:
            return Response(
                {"detail": "song_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response(
                {"detail": "Song not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        library.songs.add(song)
        library.sync_total_count()
        return Response(LibrarySerializer(library).data)

    @action(detail=True, methods=["post"], url_path="remove-song")
    def remove_song(self, request, pk=None):
        """POST /api/libraries/{id}/remove-song/ — remove a song from the library."""
        library = self.get_object()
        song_id = request.data.get("song_id")
        if not song_id:
            return Response(
                {"detail": "song_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response(
                {"detail": "Song not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        library.songs.remove(song)
        library.sync_total_count()
        return Response(LibrarySerializer(library).data)
