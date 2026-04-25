from django.contrib import admin

from ..models import AIGenerationRequest


@admin.register(AIGenerationRequest)
class AIGenerationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "request_id",
        "prompt",
        "status",
        "external_task_id",
        "external_status",
        "submitted_at",
    )
    list_filter = ("status",)
    readonly_fields = ("request_id", "submitted_at")
    search_fields = ("external_task_id", "request_id")
