from rest_framework import serializers

from ..models import PlaybackSession, Song, User


class SongSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all()
    )
    playback_session_id = serializers.PrimaryKeyRelatedField(
        source="playback_session",
        queryset=PlaybackSession.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Song
        fields = [
            "id",
            "song_id",
            "user_id",
            "playback_session_id",
            "title",
            "audio_file_url",
            "generation_status",
            "created_at",
            "is_favorite",
            "is_draft",
            "share_link",
        ]
        read_only_fields = ["song_id", "created_at"]
