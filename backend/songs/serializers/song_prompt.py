from rest_framework import serializers

from ..models import Song, SongPrompt


class SongPromptSerializer(serializers.ModelSerializer):
    song_id = serializers.PrimaryKeyRelatedField(
        source="song", queryset=Song.objects.all()
    )

    class Meta:
        model = SongPrompt
        fields = [
            "id",
            "prompt_id",
            "song_id",
            "title",
            "occasion",
            "mood_and_tone",
            "singer_tone",
            "description",
        ]
        read_only_fields = ["prompt_id"]
