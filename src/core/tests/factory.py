import os
import random
from factory import LazyAttribute, SubFactory, Faker
from factory.django import DjangoModelFactory
from django.core.files.base import ContentFile
from core.models import Object
from users.tests.factory import ProfileFactory

from django.conf import settings

BASE_COLLECTION_DIR = settings.ROOT_DIR + "collection/"


def choose_random_object_file(_):
    """
    Randomly selects a file from the test_files folder.
    """
    objects_dir = os.path.join(BASE_COLLECTION_DIR, "objects/")
    files = [
        f
        for f in os.listdir(objects_dir)
        if os.path.isfile(os.path.join(objects_dir, f))
    ]
    file = random.choice(files)
    return ContentFile(
        open(
            os.path.join(BASE_COLLECTION_DIR + "objects/", file),
            "rb",
        ).read(),
        name=file,
    )


class ObjectFactory(DjangoModelFactory):
    class Meta:
        model = Object

    owner = SubFactory(ProfileFactory)

    # Randomly select a file from the test_files folder for the source field
    source = LazyAttribute(choose_random_object_file)

    title = Faker("sentence", nb_words=3)
    # Scale is a string of 2 floats from 0 to 2, separated by a space
    scale = LazyAttribute(
        lambda _: f"{round(random.uniform(0.5, 2), 3)} {round(random.uniform(0.5, 2), 3)}"
    )
    position = LazyAttribute(
        lambda _: f"{round(random.uniform(-1, 1), 3)} {round(random.uniform(-1, 1), 3)} 0"
    )
    rotation = "270 0 0"
    file_size = Faker("random_int", min=1000, max=1_000_000)
