from django.test import TestCase

from core.management.commands.generate_artworks import (
    Command as GenerateArtworksCommand,
)
from core.management.commands.generate_exhibits import (
    Command as GenerateExhibitsCommand,
)
from core.management.commands.generate_markers import Command as GenerateMarkersCommand
from core.management.commands.generate_objects import Command as GenerateObjectsCommand
from core.models import Artwork, Exhibit, Marker, Object


class TestGenerateObjectsCommand(TestCase):
    def test_generate_objects_parser(self):
        """Test to ensure the add_arguments function is covered."""
        command = GenerateObjectsCommand()
        parser = command.create_parser("manage.py", "generate_objects")
        command.add_arguments(parser)

    def test_generate_objects_command(self):
        """Generating a single object should work."""
        command = GenerateObjectsCommand()
        command.handle(count=1)
        # Check if an object was created
        self.assertEqual(Object.objects.count(), 1)
        obj = Object.objects.first()
        self.assertIsNotNone(obj)
        self.assertIsNotNone(obj.owner)
        self.assertIsNotNone(obj.title)
        self.assertIsNotNone(obj.source)
        self.assertIsNotNone(obj.file_extension)
        self.assertIsNotNone(obj.file_name_original)
        self.assertIsNotNone(obj.file_size)

    def test_generate_multiple(self):
        """Generating multiple objects should work."""
        command = GenerateObjectsCommand()
        command.handle(count=5)
        # Check if 5 objects were created
        self.assertEqual(Object.objects.count(), 5)
        for obj in Object.objects.all():
            self.assertIsNotNone(obj.owner)
            self.assertIsNotNone(obj.title)
            self.assertIsNotNone(obj.source)
            self.assertIsNotNone(obj.file_extension)
            self.assertIsNotNone(obj.file_name_original)
            self.assertIsNotNone(obj.file_size)


class TestGenerateMarkersCommand(TestCase):
    def test_generate_markers_parser(self):
        """Test to ensure the add_arguments function is covered."""
        command = GenerateMarkersCommand()
        parser = command.create_parser("manage.py", "generate_markers")
        command.add_arguments(parser)

    def test_generate_markers_command(self):
        """Generating a single marker should work."""
        command = GenerateMarkersCommand()
        command.handle(count=1)
        # Check if a marker was created
        self.assertEqual(Marker.objects.count(), 1)
        marker = Marker.objects.first()
        self.assertIsNotNone(marker)
        self.assertIsNotNone(marker.title)

    def test_generate_multiple_markers(self):
        """Generating multiple markers should work."""
        command = GenerateMarkersCommand()
        command.handle(count=3)
        # Check if 3 markers were created
        self.assertEqual(Marker.objects.count(), 3)
        for marker in Marker.objects.all():
            self.assertIsNotNone(marker.title)


class TestGenerateArtworksCommand(TestCase):
    def test_generate_artworks_parser(self):
        """Test to ensure the add_arguments function is covered."""
        command = GenerateArtworksCommand()
        parser = command.create_parser("manage.py", "generate_artworks")
        command.add_arguments(parser)

    def test_generate_artworks_command(self):
        """Generating a single artwork should work."""
        command = GenerateArtworksCommand()
        command.handle(count=1)
        # Check if an artwork was created
        self.assertEqual(Artwork.objects.count(), 1)
        artwork = Artwork.objects.first()
        self.assertIsNotNone(artwork)
        self.assertIsNotNone(artwork.title)
        self.assertIsNotNone(artwork.description)
        self.assertEqual(
            Object.objects.count(), 1
        )  # Ensure an object is created as well
        self.assertEqual(
            Marker.objects.count(), 1
        )  # Ensure a marker is created as well
        self.assertIsNotNone(artwork.augmented)
        self.assertIsNotNone(artwork.marker)

    def test_generate_multiple_artworks(self):
        """Generating multiple artworks should work."""
        command = GenerateArtworksCommand()
        command.handle(count=10)
        # Check if 10 artworks were created
        self.assertEqual(Artwork.objects.count(), 10)
        for artwork in Artwork.objects.all():
            self.assertIsNotNone(artwork.title)
            self.assertIsNotNone(artwork.description)
            self.assertIsNotNone(artwork.augmented)
            self.assertIsNotNone(artwork.marker)
        self.assertEqual(Object.objects.count(), 10)
        self.assertEqual(Marker.objects.count(), 10)


class TestGenerateExhibitsCommand(TestCase):
    def test_generate_exhibits_parser(self):
        """Test to ensure the add_arguments function is covered."""
        command = GenerateExhibitsCommand()
        parser = command.create_parser("manage.py", "generate_exhibits")
        command.add_arguments(parser)

    def test_generate_exhibits_command(self):
        """Generating a single exhibit should work."""
        command = GenerateExhibitsCommand()
        command.handle(count=1)
        # Check if an exhibit was created
        self.assertEqual(Exhibit.objects.count(), 1)
        exhibit = Exhibit.objects.first()
        self.assertIsNotNone(exhibit)
        self.assertIsNotNone(exhibit.name)
        self.assertIsNotNone(exhibit.artworks)
        self.assertGreater(
            exhibit.artworks.count(), 0
        )  # Ensure at least one artwork is associated

    def test_generate_multiple_exhibits(self):
        """Generating multiple exhibits should work."""
        command = GenerateExhibitsCommand()
        command.handle(count=3)
        # Check if 3 exhibits were created
        self.assertEqual(Exhibit.objects.count(), 3)
        for exhibit in Exhibit.objects.all():
            self.assertIsNotNone(exhibit.name)
            self.assertGreater(exhibit.artworks.count(), 0)
