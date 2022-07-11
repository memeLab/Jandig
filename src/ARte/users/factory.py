from factory.django import DjangoModelFactory

from .models import Object
from django.contrib.auth.models import User


class UserFactory(DjangoModelFactory):
    username = "Testador"
    email = "testador@memelab.com"

    class Meta:
        model = User


class ObjectFactory(DjangoModelFactory):
    id = 1
    source = "objects/osaka.gif"
    owner = "Matheus"
    author = "Matheus"
    uploaded_at = (2020, 11, 25, 14, 30, 0)
    title = "osaka"
    position = "0 0 0"
    scale = "1 1"
    rotation = "270 0 0"

    class Meta:

        model = Object
