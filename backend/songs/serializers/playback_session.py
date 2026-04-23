from rest_framework import serializers

from ..models import PlaybackSession


class PlaybackSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaybackSession
        fields = [
            "id",
            "session_id",
            "current_position",
            "loop_start",
            "loop_end",
            "equalizer_settings",
        ]
        read_only_fields = ["session_id"]
