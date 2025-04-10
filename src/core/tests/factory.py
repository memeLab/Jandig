import os
import random
from factory import LazyAttribute, SubFactory, Faker, post_generation
from factory.django import DjangoModelFactory
from django.core.files.base import ContentFile
from core.models import Object, Marker, Artwork, Exhibit
from users.tests.factory import ProfileFactory

from django.conf import settings

BASE_COLLECTION_DIR = settings.ROOT_DIR + "collection/"


def choose_random_object_file(_):
    """
    Randomly selects a file from the collection/objects folder.
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
            os.path.join(objects_dir, file),
            "rb",
        ).read(),
        name=file,
    )


def choose_random_marker_file(_):
    """
    Randomly selects a file from the collection/markers folder.
    """
    markers_dir = os.path.join(BASE_COLLECTION_DIR, "markers/")
    files = [
        f
        for f in os.listdir(markers_dir)
        if os.path.isfile(os.path.join(markers_dir, f))
    ]
    file = random.choice(files)
    return ContentFile(
        open(
            os.path.join(markers_dir, file),
            "rb",
        ).read(),
        name=file,
    )


def chose_random_patt_file(_):
    """
    Randomly selects a file from the collection/patts folder.
    """
    patts_dir = os.path.join(BASE_COLLECTION_DIR, "patts/")
    files = [
        f for f in os.listdir(patts_dir) if os.path.isfile(os.path.join(patts_dir, f))
    ]
    file = random.choice(files)
    return ContentFile(
        open(
            os.path.join(patts_dir, file),
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

    author = Faker("name")
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


class MarkerFactory(DjangoModelFactory):
    class Meta:
        model = Marker

    owner = SubFactory(ProfileFactory)

    # Randomly select a file from the test_files folder for the source field
    source = LazyAttribute(choose_random_marker_file)
    patt = LazyAttribute(chose_random_patt_file)

    title = Faker("sentence", nb_words=3)
    author = Faker("name")

    file_size = Faker("random_int", min=1000, max=1_000_000)


class ArtworkFactory(DjangoModelFactory):
    class Meta:
        model = Artwork

    author = SubFactory(ProfileFactory)  # Use ProfileFactory for the author
    marker = SubFactory(MarkerFactory)  # Use MarkerFactory for the marker
    augmented = SubFactory(ObjectFactory)  # Use ObjectFactory for the augmented object

    title = Faker("sentence", nb_words=3)  # Generate a random title
    description = Faker("text", max_nb_chars=200)  # Generate a random description


class ExhibitFactory(DjangoModelFactory):
    class Meta:
        model = Exhibit

    owner = SubFactory(ProfileFactory)  # Use ProfileFactory for the owner
    name = Faker("sentence", nb_words=3)  # Generate a random unique name
    slug = LazyAttribute(
        lambda obj: obj.name.lower().replace(" ", "-")
    )  # Generate a slug based on the name

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        artworks_data = kwargs.pop("artworks", [])
        instance = super()._create(model_class, *args, **kwargs)
        if artworks_data:
            instance.artworks.set(artworks_data)
        return instance

    @post_generation
    def artworks(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.artworks.set(extracted)
        else:
            self.artworks.set(
                [
                    ArtworkFactory(author=self.owner)
                    for _ in range(random.randint(1, 15))
                ]
            )
