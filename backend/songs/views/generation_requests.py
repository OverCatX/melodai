from django.core.exceptions import ImproperlyConfigured
from django.db import IntegrityError, transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..generation.service import refresh_generation_status, run_generation
from ..models import AIGenerationRequest
from ..serializers import AIGenerationRequestSerializer


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

    @action(detail=True, methods=["post"], url_path="run")
    def run(self, request, pk=None):
        """POST /api/generation-requests/{id}/run/ — execute configured generator strategy."""
        ai_request = self.get_object()
        try:
            run_generation(ai_request)
        except ImproperlyConfigured as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        ai_request.refresh_from_db()
        serializer = self.get_serializer(ai_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
