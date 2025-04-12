from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from users.models import Profile
from users.serializers import ProfileSerializer


class ProfileViewset(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.select_related("user").all().order_by("id")
