import factory
from factory.django import DjangoModelFactory

from django.contrib.auth.models import Object

class ObjectFactory(DjangoModelFactory):
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