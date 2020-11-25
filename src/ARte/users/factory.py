import factory
from factory.django import DjangoModelFactory

from django.contrib.auth.models import User

class UserFactory(DjangoModelFactory):
    username = 'Testador'
    email = 'testador@memelab.com'

    class Meta:
        model = User