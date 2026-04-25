from django.contrib import admin

from ..models import SongPrompt


class SongPromptInline(admin.StackedInline):
    model = SongPrompt
    extra = 0
    can_delete = False
    readonly_fields = ("prompt_id",)
