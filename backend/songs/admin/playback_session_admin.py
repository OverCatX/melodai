from django.contrib import admin

from ..models import PlaybackSession


@admin.register(PlaybackSession)
class PlaybackSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "current_position", "loop_start", "loop_end")
    readonly_fields = ("session_id",)
