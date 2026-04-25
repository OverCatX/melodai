from django.contrib import admin

from ..models import SharedSong


class SharedSongInline(admin.StackedInline):
    model = SharedSong
    extra = 0
    can_delete = True
    readonly_fields = ("share_id", "shared_at")
