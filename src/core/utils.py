import uuid

from django.urls import reverse


def generate_uuid_name():
    """Generate a UUID4 name"""

    return str(uuid.uuid4())  # Use uuid4 for a random unique identifier


def get_admin_url():
    """Get the admin URL"""
    # Can't be done as constant, since this IS the admin file, asking reverse("admin:index") causes admin to not load
    return reverse("admin:index")
