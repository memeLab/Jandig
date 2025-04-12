from django.contrib.auth.models import User
from django.db.models.signals import post_save
from factory import Faker, Sequence, SubFactory, django
from factory.django import DjangoModelFactory

from users.models import Profile


def generate_username():
    """
    Generates a random username using the Faker library.
    """
    prefix = Faker("prefix").evaluate(None, 0, {"locale": "en-US"})
    first_name = Faker("first_name").evaluate(None, 0, {"locale": "en-US"})
    last_name = Faker("last_name").evaluate(None, 0, {"locale": "en-US"})
    suffix = Faker("suffix").evaluate(None, 0, {"locale": "en-US"})
    return f"{prefix.lower()}{first_name.lower()}{last_name.lower()}{suffix.lower()}"


@django.mute_signals(post_save)
class UserFactory(DjangoModelFactory):
    username = Sequence(lambda n: f"{generate_username()}_{n}")
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
