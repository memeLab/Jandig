from core.models import Exhibit
from rest_framework.serializers import ModelSerializer


class ExhibitSerializer(ModelSerializer):
    class Meta:
        model = Exhibit
        fields = ("id", "owner", "name", "slug", "artworks", "creation_date")
        read_only_fields = (
            "id",
            "creation_date",
        )
