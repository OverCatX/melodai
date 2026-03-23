from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    formed_year = models.PositiveSmallIntegerField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='artists', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='albums'
    )
    release_date = models.DateField(null=True, blank=True)
    cover_image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date', 'title']
        unique_together = ('title', 'artist')

    def __str__(self):
        return f"{self.title} – {self.artist}"


class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(
        Artist, on_delete=models.CASCADE, related_name='songs'
    )
    album = models.ForeignKey(
        Album, on_delete=models.SET_NULL, null=True, blank=True, related_name='songs'
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, null=True, blank=True, related_name='songs'
    )
    duration_seconds = models.PositiveIntegerField(
        help_text="Song duration in seconds",
        validators=[MinValueValidator(1)]
    )
    track_number = models.PositiveSmallIntegerField(null=True, blank=True)
    lyrics = models.TextField(blank=True)
    audio_file_url = models.URLField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['artist', 'album', 'track_number', 'title']

    def __str__(self):
        return f"{self.title} by {self.artist}"

    @property
    def duration_display(self):
        minutes, seconds = divmod(self.duration_seconds, 60)
        return f"{minutes}:{seconds:02d}"


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    songs = models.ManyToManyField(
        Song,
        through='PlaylistEntry',
        related_name='playlists',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PlaylistEntry(models.Model):
    playlist = models.ForeignKey(
        Playlist, on_delete=models.CASCADE, related_name='entries'
    )
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE, related_name='playlist_entries'
    )
    position = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['playlist', 'position']
        unique_together = ('playlist', 'position')

    def __str__(self):
        return f"{self.playlist} – #{self.position}: {self.song}"
