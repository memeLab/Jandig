from django.core.management.base import BaseCommand

from core.tests.factory import ExhibitFactory
from users.tests.factory import ProfileFactory


class Command(BaseCommand):
    help = "Generate N exhibits for local development"

    def add_arguments(self, parser):
        # Add an argument to specify the number of exhibits to create
        parser.add_argument(
            "count",
            type=int,
            help="The number of exhibits to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        self.stdout.write(f"Generating {count} exhibits...")
        author = ProfileFactory()
        self.stdout.write(f"Using owner: {author.user.username}")
        for i in range(count):
            obj = ExhibitFactory(owner=author)
            self.stdout.write(f"Created Exhibit {i + 1}: {obj.name} (ID: {obj.id})")

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} exhibits!"))
