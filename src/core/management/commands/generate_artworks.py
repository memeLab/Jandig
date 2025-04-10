from django.core.management.base import BaseCommand
from core.tests.factory import ArtworkFactory, MarkerFactory, ObjectFactory
from users.tests.factory import ProfileFactory
import random


class Command(BaseCommand):
    help = "Generate N artworks for local development"

    def add_arguments(self, parser):
        # Add an argument to specify the number of artworks to create
        parser.add_argument(
            "count",
            type=int,
            help="The number of artworks to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        self.stdout.write(f"Generating {count} artworks...")
        author = ProfileFactory()
        self.stdout.write(f"Using owner: {author.user.username}")
        for i in range(count):
            # Randomly decides if the artwork owner is the same owner of the marker, object, both or none
            random_choice = random.choice([0, 1, 2, 3])
            match random_choice:
                case 0:
                    self.stdout.write(
                        "This artwork Marker and Object are not owned by the Artwork author"
                    )
                    # owner of neither
                    obj = ArtworkFactory()
                case 1:
                    self.stdout.write(
                        "This artwork Marker is owned by the Artwork author"
                    )
                    # owner of marker
                    marker = MarkerFactory(owner=author)
                    obj = ArtworkFactory(author=author, marker=marker)
                case 2:
                    self.stdout.write(
                        "This artwork Object is owned by the Artwork author"
                    )
                    # owner of object
                    augmented = ObjectFactory(owner=author)
                    obj = ArtworkFactory(author=author, augmented=augmented)
                case 3:
                    self.stdout.write(
                        "This artwork Marker and Object are owned by the Artwork author"
                    )
                    # owner of both
                    marker = MarkerFactory(owner=author)
                    augmented = ObjectFactory(owner=author)
                    obj = ArtworkFactory(
                        author=author, marker=marker, augmented=augmented
                    )
            self.stdout.write(f"Created Artwork {i + 1}: {obj.title} (ID: {obj.id})")

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} artworks!"))
