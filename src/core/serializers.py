from rest_framework.serializers import ModelSerializer, SerializerMethodField

from core.models import Artwork, Exhibit, Marker, Object
from users.serializers import ProfileSerializer


class MarkerSerializer(ModelSerializer):
    owner = ProfileSerializer(read_only=True)

    source_size = SerializerMethodField()

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
            "source_size",
            "artworks_count",
            "exhibits_count",
        )
        read_only_fields = (
            "id",
            "uploaded_at",
        )

    def get_source_size(self, obj):
        return obj.source.size


class ObjectSerializer(ModelSerializer):
    owner = ProfileSerializer(read_only=True)
    source_size = SerializerMethodField()

    class Meta:
        model = Object
        fields = (
            "id",
            "owner",
            "source",
            "source_size",
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

    def get_source_size(self, obj):
        return obj.source.size


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
    class Meta:
        model = Exhibit
        fields = ("id", "owner", "name", "slug", "artworks", "creation_date")
        read_only_fields = (
            "id",
            "creation_date",
        )
