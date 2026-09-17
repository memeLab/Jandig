import uuid

from django.urls import reverse


def filesizeformat(value):
    """Format a file size in bytes to a human-readable string."""
    try:
        size = float(value)
    except (TypeError, ValueError):
        return "0 B"
    if size < 1024:
        return f"{int(size)} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"


def generate_uuid_name():
    """Generate a UUID4 name"""

    return str(uuid.uuid4())  # Use uuid4 for a random unique identifier


def get_admin_url():
    """Get the admin URL"""
    # Can't be done as constant, since this IS the admin file, asking reverse("admin:index") causes admin to not load
    return reverse("admin:index")
