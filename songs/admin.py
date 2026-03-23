from django.contrib import admin
from .models import Genre, Artist, Album, Song, Playlist, PlaylistEntry


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


class AlbumInline(admin.TabularInline):
    model = Album
    extra = 0
    fields = ('title', 'release_date')


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'formed_year', 'created_at')
    search_fields = ('name', 'country')
    filter_horizontal = ('genres',)
    inlines = [AlbumInline]


class SongInline(admin.TabularInline):
    model = Song
    extra = 0
    fields = ('track_number', 'title', 'duration_seconds', 'genre')


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'release_date')
    search_fields = ('title', 'artist__name')
    list_filter = ('release_date',)
    inlines = [SongInline]


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'genre', 'duration_display', 'release_date')
    search_fields = ('title', 'artist__name', 'album__title')
    list_filter = ('genre', 'release_date')
    readonly_fields = ('duration_display',)


class PlaylistEntryInline(admin.TabularInline):
    model = PlaylistEntry
    extra = 0
    fields = ('position', 'song', 'added_at')
    readonly_fields = ('added_at',)
    ordering = ('position',)


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = [PlaylistEntryInline]
