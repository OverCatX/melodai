from rest_framework import viewsets

from ..models import Draft
from ..serializers import DraftSerializer


class DraftViewSet(viewsets.ModelViewSet):
    """
    CRUD for Draft.
    list   GET    /api/drafts/
    create POST   /api/drafts/
    read   GET    /api/drafts/{id}/
    update PUT    /api/drafts/{id}/
    patch  PATCH  /api/drafts/{id}/
    delete DELETE /api/drafts/{id}/
    """

    queryset = Draft.objects.select_related("song").all()
    serializer_class = DraftSerializer
