from rest_framework import serializers

from ..models import Library, Song, User


class LibrarySerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all()
    )
    song_ids = serializers.PrimaryKeyRelatedField(
        source="songs",
        queryset=Song.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Library
        fields = [
            "id",
            "user_id",
            "song_ids",
            "filter_criteria",
            "total_count",
        ]
        read_only_fields = ["total_count"]

    def create(self, validated_data):
        songs = validated_data.pop("songs", [])
        library = Library.objects.create(**validated_data)
        library.songs.set(songs)
        library.sync_total_count()
        return library

    def update(self, instance, validated_data):
        songs = validated_data.pop("songs", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if songs is not None:
            instance.songs.set(songs)
            instance.sync_total_count()
        return instance
