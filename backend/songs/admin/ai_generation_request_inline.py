from django.contrib import admin

from ..models import AIGenerationRequest


class AIGenerationRequestInline(admin.StackedInline):
    model = AIGenerationRequest
    extra = 0
    can_delete = False
    readonly_fields = ("request_id", "submitted_at")
