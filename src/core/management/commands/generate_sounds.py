from django.core.management.base import BaseCommand

from core.tests.factory import SoundFactory
from users.tests.factory import ProfileFactory


class Command(BaseCommand):
    help = "Generate N sounds for local development"

    def add_arguments(self, parser):
        # Add an argument to specify the number of sounds to create
        parser.add_argument(
            "count",
            type=int,
            help="The number of sounds to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        self.stdout.write(f"Generating {count} sounds...")
        owner = ProfileFactory()
        self.stdout.write(f"Using owner: {owner.user.username}")
        for i in range(count):
            obj = SoundFactory(owner=owner)
            self.stdout.write(f"Created Object {i + 1}: {obj.title} (ID: {obj.id})")

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} sounds!"))
