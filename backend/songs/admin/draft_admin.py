from django.contrib import admin

from ..models import Draft


@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display = ("song", "saved_at", "is_submitted", "retention_policy")
    list_filter = ("is_submitted",)
    readonly_fields = ("draft_id", "saved_at")
