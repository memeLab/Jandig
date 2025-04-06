from rest_framework.serializers import ModelSerializer

from core.models import Artwork, Exhibit, Marker, Object
from users.serializers import ProfileSerializer


class MarkerSerializer(ModelSerializer):
    owner = ProfileSerializer(read_only=True)

    class Meta:
        model = Marker
        fields = (
            "id",
            "owner",
            "source",
            "uploaded_at",
            "author",
            "title",
            "patt",
            "file_size",
            "artworks_count",
            "exhibits_count",
        )
        read_only_fields = (
            "id",
            "uploaded_at",
        )


class ObjectSerializer(ModelSerializer):
    owner = ProfileSerializer(read_only=True)

    class Meta:
        model = Object
        fields = (
            "id",
            "owner",
            "source",
            "file_size",
            "uploaded_at",
            "author",
            "title",
            "scale",
            "position",
            "rotation",
            "artworks_count",
            "exhibits_count",
        )
        read_only_fields = (
            "id",
            "uploaded_at",
        )


class ArtworkSerializer(ModelSerializer):
    marker = MarkerSerializer(read_only=True)
    augmented = ObjectSerializer(read_only=True)
    author = ProfileSerializer(read_only=True)

    class Meta:
        model = Artwork
        fields = (
            "id",
            "author",
            "marker",
            "augmented",
            "title",
            "description",
            "created_at",
            "exhibits_count",
        )
        read_only_fields = (
            "id",
            "uploaded_at",
        )


class ExhibitSerializer(ModelSerializer):
    artworks = ArtworkSerializer(many=True, read_only=True)

    class Meta:
        model = Exhibit
        fields = ("id", "owner", "name", "slug", "artworks", "creation_date")
        read_only_fields = (
            "id",
            "creation_date",
        )
