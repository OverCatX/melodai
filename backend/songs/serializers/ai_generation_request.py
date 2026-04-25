from rest_framework import serializers

from ..models import AIGenerationRequest, SongPrompt


class AIGenerationRequestSerializer(serializers.ModelSerializer):
    prompt_id = serializers.PrimaryKeyRelatedField(
        source="prompt", queryset=SongPrompt.objects.all()
    )
    # Same id as GET /api/songs/{id}/ and …/songs/{id}/download/ — not the same as "id" above.
    song_id = serializers.IntegerField(source="prompt.song_id", read_only=True)

    class Meta:
        model = AIGenerationRequest
        fields = [
            "id",
            "request_id",
            "song_id",
            "prompt_id",
            "submitted_at",
            "status",
            "error_message",
            "external_task_id",
            "external_status",
        ]
        read_only_fields = ["request_id", "submitted_at", "song_id"]
