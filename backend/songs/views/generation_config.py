from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..generation.factory import (
    VALID_STRATEGY_NAMES,
    clear_runtime_generator_name,
    get_effective_generator_name,
    set_runtime_generator_name,
    strategy_source,
)


def _payload():
    return {
        "generator_strategy": get_effective_generator_name(),
        "strategy_source": strategy_source(),
        "environment_default": (getattr(settings, "GENERATOR_STRATEGY", "mock") or "mock").lower(),
        "suno_api_configured": bool(getattr(settings, "SUNO_API_KEY", "") or ""),
    }


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def generation_config(request):
    """
    GET: active strategy + whether Suno key exists (no secrets).
    POST: set runtime strategy ({generator_strategy}) or
          {clear_runtime_override: true} to revert to the server default.
    """
    if request.method == "GET":
        return Response(_payload())

    data = request.data if isinstance(request.data, dict) else {}
    if data.get("clear_runtime_override"):
        clear_runtime_generator_name()
        return Response(_payload())

    name = (data.get("generator_strategy") or "").strip().lower()
    if name not in VALID_STRATEGY_NAMES:
        return Response(
            {"detail": "generator_strategy must be 'mock' or 'suno'."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    set_runtime_generator_name(name)
    return Response(_payload())
