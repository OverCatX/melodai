from django.contrib import admin

from ..models import SharedSong


@admin.register(SharedSong)
class SharedSongAdmin(admin.ModelAdmin):
    list_display = ("song", "share_link", "shared_at", "accessible_by_guest")
    list_filter = ("accessible_by_guest",)
    readonly_fields = ("share_id", "shared_at")
