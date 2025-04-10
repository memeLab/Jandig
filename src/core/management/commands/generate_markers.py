from django.core.management.base import BaseCommand
from core.tests.factory import MarkerFactory
from users.tests.factory import ProfileFactory


class Command(BaseCommand):
    help = "Generate N markers for local development"

    def add_arguments(self, parser):
        # Add an argument to specify the number of markers to create
        parser.add_argument(
            "count",
            type=int,
            help="The number of markers to create",
        )

    def handle(self, *args, **options):
        count = options["count"]

        self.stdout.write(f"Generating {count} markers...")
        owner = ProfileFactory()
        self.stdout.write(f"Using owner: {owner.user.username}")
        for i in range(count):
            obj = MarkerFactory(owner=owner)
            self.stdout.write(f"Created Marker {i + 1}: {obj.title} (ID: {obj.id})")

        self.stdout.write(self.style.SUCCESS(f"Successfully created {count} markers!"))
