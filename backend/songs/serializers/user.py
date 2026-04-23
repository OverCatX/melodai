from rest_framework import serializers

from ..models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "user_id",
            "google_id",
            "email",
            "display_name",
            "session_token",
        ]
        read_only_fields = ["user_id"]
