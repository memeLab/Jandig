from core.models import Artwork
from rest_framework.serializers import ModelSerializer


class ArtworkSerializer(ModelSerializer):
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
        )
        read_only_fields = (
            "id",
            "uploaded_at",
        )
