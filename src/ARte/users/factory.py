import factory
from factory.django import DjangoModelFactory

from .models import Object
from django.contrib.auth.models import User

class UserFactory(DjangoModelFactory):
    username = 'Testador'
    email = 'test2019ador@gmail.com'

    class Meta:
        model = User

class ObjectFactory(DjangoModelFactory):
    id = 1
    owner = 'Matheus'
    source = 'objects/osaka.gif'
    uploaded_at = (2020, 11, 25, 14, 30, 0)
    author = 'Matheus'
    title = 'osaka'
    scale = '1 1'
    position = '0 0 0'
    rotation = '270 0 0'

    class Meta:
        model = Object