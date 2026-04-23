from django.contrib import admin
from .models import (
    User,
    Song,
    Library,
    SongPrompt,
    AIGenerationRequest,
    SharedSong,
    PlaybackSession,
    Draft,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("display_name", "email", "google_id")
    search_fields = ("display_name", "email", "google_id")
    readonly_fields = ("user_id",)


class SongPromptInline(admin.StackedInline):
    model = SongPrompt
    extra = 0
    can_delete = False
    readonly_fields = ("prompt_id",)


class SharedSongInline(admin.StackedInline):
    model = SharedSong
    extra = 0
    can_delete = True
    readonly_fields = ("share_id", "shared_at")


class DraftInline(admin.TabularInline):
    model = Draft
    extra = 0
    readonly_fields = ("draft_id", "saved_at")


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


class SongInline(admin.TabularInline):
    model = Library.songs.through
    extra = 0
    verbose_name = "Song"
    verbose_name_plural = "Songs"


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ("user", "total_count")
    search_fields = ("user__display_name",)
    readonly_fields = ("total_count",)
    filter_horizontal = ("songs",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.sync_total_count()


class AIGenerationRequestInline(admin.StackedInline):
    model = AIGenerationRequest
    extra = 0
    can_delete = False
    readonly_fields = ("request_id", "submitted_at")


@admin.register(SongPrompt)
class SongPromptAdmin(admin.ModelAdmin):
    list_display = ("title", "song", "occasion", "mood_and_tone", "singer_tone")
    list_filter = ("occasion", "mood_and_tone", "singer_tone")
    search_fields = ("title", "song__title")
    readonly_fields = ("prompt_id",)
    inlines = [AIGenerationRequestInline]


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


@admin.register(SharedSong)
class SharedSongAdmin(admin.ModelAdmin):
    list_display = ("song", "share_link", "shared_at", "accessible_by_guest")
    list_filter = ("accessible_by_guest",)
    readonly_fields = ("share_id", "shared_at")


@admin.register(PlaybackSession)
class PlaybackSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "current_position", "loop_start", "loop_end")
    readonly_fields = ("session_id",)


@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display = ("song", "saved_at", "is_submitted", "retention_policy")
    list_filter = ("is_submitted",)
    readonly_fields = ("draft_id", "saved_at")
