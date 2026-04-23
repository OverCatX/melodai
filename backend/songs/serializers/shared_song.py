from rest_framework import serializers

from ..models import SharedSong, Song


class SharedSongSerializer(serializers.ModelSerializer):
    song_id = serializers.PrimaryKeyRelatedField(
        source="song", queryset=Song.objects.all()
    )

    class Meta:
        model = SharedSong
        fields = [
            "id",
            "share_id",
            "song_id",
            "share_link",
            "shared_at",
            "accessible_by_guest",
        ]
        read_only_fields = ["share_id", "shared_at"]
