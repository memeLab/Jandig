from core.models import Object
from rest_framework.serializers import ModelSerializer


class ObjectSerializer(ModelSerializer):
    class Meta:
        model = Object
        fields = (
            "id",
            "owner",
            "source",
            "uploaded_at",
            "author",
            "title",
            "scale",
            "position",
            "rotation",
        )
        read_only_fields = (
            "id",
            "uploaded_at",
        )
