from rest_framework.serializers import ModelSerializer, SerializerMethodField

from users.models import Profile


class ProfileSerializer(ModelSerializer):
    username = SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
        )
        read_only_fields = (
            "id",
            "uploaded_at",
        )

    def get_username(self, obj):
        return obj.user.username
