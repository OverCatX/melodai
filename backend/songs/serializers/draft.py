from rest_framework import serializers

from ..models import Draft, Song


class DraftSerializer(serializers.ModelSerializer):
    song_id = serializers.PrimaryKeyRelatedField(
        source="song", queryset=Song.objects.all()
    )

    class Meta:
        model = Draft
        fields = [
            "id",
            "draft_id",
            "song_id",
            "saved_at",
            "is_submitted",
            "retention_policy",
        ]
        read_only_fields = ["draft_id", "saved_at"]
