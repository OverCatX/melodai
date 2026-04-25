from django.contrib import admin

from ..models import Song
from .draft_inline import DraftInline
from .shared_song_inline import SharedSongInline
from .song_prompt_inline import SongPromptInline


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "generation_status",
        "is_draft",
        "is_favorite",
        "created_at",
    )
    list_filter = ("generation_status", "is_draft", "is_favorite")
    search_fields = ("title", "user__display_name")
    readonly_fields = ("song_id", "created_at")
    inlines = [SongPromptInline, SharedSongInline, DraftInline]
