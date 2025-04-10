from django.contrib.auth.models import User
from django.db.models.signals import post_save
from factory import Faker, SubFactory, django
from factory.django import DjangoModelFactory

from users.models import Profile


@django.mute_signals(post_save)
class UserFactory(DjangoModelFactory):
    username = Faker("user_name")
    email = Faker("email")

    class Meta:
        model = User


class ProfileFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    bio = Faker("text", max_nb_chars=200)
    country = Faker("country_code")
    personal_site = Faker("url")

    class Meta:
        model = Profile
