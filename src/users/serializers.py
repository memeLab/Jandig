from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import Profile


class ProfileSerializer(ModelSerializer):
    username = SerializerMethodField()

    class Meta:
        model = Profile
        fields = ("id", "username", "user_id")
        read_only_fields = (
            "id",
            "uploaded_at",
        )

    def get_username(self, obj):
        return obj.user.username

    def get_user_id(self, obj):
        return obj.user.id


class JandigJWTSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["user_profile_id"] = user.profile.id
        token["user_id"] = user.id
        token["username"] = user.username
        return token
