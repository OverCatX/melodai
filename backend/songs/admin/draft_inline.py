from django.contrib import admin

from ..models import Draft


class DraftInline(admin.TabularInline):
    model = Draft
    extra = 0
    readonly_fields = ("draft_id", "saved_at")
