from django.contrib import admin

from ..models import SongPrompt
from .ai_generation_request_inline import AIGenerationRequestInline


@admin.register(SongPrompt)
class SongPromptAdmin(admin.ModelAdmin):
    list_display = ("title", "song", "occasion", "mood_and_tone", "singer_tone")
    list_filter = ("occasion", "mood_and_tone", "singer_tone")
    search_fields = ("title", "song__title")
    readonly_fields = ("prompt_id",)
    inlines = [AIGenerationRequestInline]
