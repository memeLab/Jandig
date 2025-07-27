from rest_framework.serializers import IntegerField, ModelSerializer

from core.models import Artwork, Exhibit, Marker, Object
from users.serializers import ProfileSerializer


class MarkerSerializer(ModelSerializer):
    owner = ProfileSerializer(read_only=True)
    exhibits_count = IntegerField(read_only=True)

    class Meta:
        model = Marker
        fields = (
            "id",
            "owner",
            "source",
            "created",
            "author",
            "title",
            "patt",
            "file_size",
            "artworks_count",
            "exhibits_count",
        )
        read_only_fields = (
            "id",
            "created",
        )


class ObjectSerializer(ModelSerializer):
    owner = ProfileSerializer(read_only=True)
    exhibits_count = IntegerField(read_only=True)

    class Meta:
        model = Object
        fields = (
            "id",
            "owner",
            "source",
            "file_size",
            "created",
            "author",
            "title",
            "artworks_count",
            "exhibits_count",
        )
        read_only_fields = (
            "id",
            "created",
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
            "created",
            "exhibits_count",
            "scale_x",
            "scale_y",
            "position_x",
            "position_y",
        )
        read_only_fields = (
            "id",
            "created",
        )


class ExhibitSerializer(ModelSerializer):
    artworks = ArtworkSerializer(many=True, read_only=True)
    augmenteds = ObjectSerializer(many=True, read_only=True)

    class Meta:
        model = Exhibit
        fields = ("id", "owner", "name", "slug", "artworks", "augmenteds", "created")
        read_only_fields = (
            "id",
            "created",
        )
