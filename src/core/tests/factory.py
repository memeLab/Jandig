import os
import random

from django.conf import settings
from django.core.files.base import ContentFile
from factory import Faker, LazyAttribute, SubFactory, post_generation
from factory.django import DjangoModelFactory

from core.models import Artwork, Exhibit, ExhibitTypes, Marker, Object, Sound
from users.tests.factory import ProfileFactory

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


def choose_random_sound_file(_):
    """
    Randomly selects a file from the collection/sounds folder.
    """
    sounds_dir = os.path.join(BASE_COLLECTION_DIR, "sounds/")
    files = [
        f for f in os.listdir(sounds_dir) if os.path.isfile(os.path.join(sounds_dir, f))
    ]
    file = random.choice(files)
    return ContentFile(
        open(
            os.path.join(sounds_dir, file),
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

    file_size = Faker("random_int", min=1000, max=1_000_000)
    file_name_original = Faker("slug")
    file_extension = LazyAttribute(lambda obj: obj.source.name.split(".")[-1])


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

    scale_x = LazyAttribute(lambda _: round(random.uniform(0.1, 5), 2))
    scale_y = LazyAttribute(lambda _: round(random.uniform(0.1, 5), 2))
    position_x = LazyAttribute(lambda _: round(random.uniform(-2, 2), 2))
    position_y = LazyAttribute(lambda _: round(random.uniform(-2, 2), 2))


class ExhibitFactory(DjangoModelFactory):
    class Meta:
        model = Exhibit
        skip_postgeneration_save = True

    owner = SubFactory(ProfileFactory)  # Use ProfileFactory for the owner
    name = Faker("sentence", nb_words=3)  # Generate a random unique name
    slug = LazyAttribute(
        lambda obj: obj.name.lower().replace(" ", "-").replace(".", "")
    )  # Generate a slug based on the name

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        artworks_data = kwargs.pop("artworks", [])
        augmenteds_data = kwargs.pop("augmenteds", [])
        instance = super()._create(model_class, *args, **kwargs)
        if artworks_data:
            instance.artworks.set(artworks_data)
        if augmenteds_data:
            instance.augmenteds.set(augmenteds_data)
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
                    for _ in range(random.randint(1, 10))
                ]
            )

    @post_generation
    def augmenteds(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.augmenteds.set(extracted)
        else:
            augmented = random.randint(0, 5)
            self.augmenteds.set(
                [ObjectFactory(owner=self.owner) for _ in range(augmented)]
            )
            if augmented > 0:
                self.exhibit_type = ExhibitTypes.MR
                self.save()


class SoundFactory(DjangoModelFactory):
    class Meta:
        model = Sound

    owner = SubFactory(ProfileFactory)
    file = LazyAttribute(choose_random_sound_file)
    title = Faker("sentence", nb_words=3)
    author = Faker("name")
