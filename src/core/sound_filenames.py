"""Move sound files stored under their uploader's filename to generated names.

See #991. New uploads already land at `sounds/<uuid>.<ext>` (#982); the rows
that predate it still point at files named by their uploader. The deployments
have no console, so this runs from the Sound admin (an action plus a filter)
rather than from a management command.
"""

from django.core.files.base import ContentFile

from core.models import sound_file_path

# What `sound_file_path` produces: sounds/<32 hex chars>[.ext]
GENERATED_NAME_REGEX = r"^sounds/[0-9a-f]{32}([.][A-Za-z0-9]+)?$"


def with_generated_name(queryset):
    """Sounds whose file already has a generated name."""
    return queryset.filter(file__regex=GENERATED_NAME_REGEX)


def with_legacy_name(queryset):
    """Sounds whose file is still stored under a user-supplied name."""
    return queryset.exclude(file="").exclude(file__regex=GENERATED_NAME_REGEX)


def rename_to_generated_name(sound):
    """Write the new object, point the row at it, then drop the old one.

    The order matters. Interrupted between any two steps, the worst outcome is
    an orphaned old object, never a row pointing at a key that no longer
    exists. Returns the new name.
    """
    old_name = sound.file.name
    storage = sound.file.storage
    with sound.file.open("rb") as handle:
        content = handle.read()

    if not sound.file_name_original:
        sound.file_name_original = old_name.rsplit("/", 1)[-1]

    # FileField.save writes through storage and resets the cached handle.
    sound.file.save(sound_file_path(sound, old_name), ContentFile(content), save=True)
    new_name = sound.file.name

    if old_name != new_name and storage.exists(old_name):
        storage.delete(old_name)
    return new_name
