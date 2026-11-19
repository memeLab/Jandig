"""Move sound files stored under their uploader's filename to generated names.

See #991. New uploads already land at `sounds/<uuid>.<ext>` (#982); the rows
that predate it still point at files named by their uploader. The deployments
have no console, so this runs from the Sound admin (an action plus a filter)
rather than from a management command.
"""

import logging

from django.core.files.base import ContentFile
from django.db import transaction

log = logging.getLogger(__name__)

# What `sound_file_path` produces: sounds/<32 hex chars>[.<ext>]. The extension
# is whatever followed the last dot of the upload, so it is not restricted to
# letters and digits: a name this pattern missed would be renamed on every run.
GENERATED_NAME_REGEX = r"^sounds/[0-9a-f]{32}([.][^/]*)?$"


class OldFileNotRemoved(Exception):
    """The sound was renamed, but its old file is still in storage."""

    def __init__(self, old_name, new_name):
        super().__init__(f"{old_name} was renamed to {new_name} but not removed")
        self.old_name = old_name
        self.new_name = new_name


def with_generated_name(queryset):
    """Sounds whose file already has a generated name."""
    return queryset.filter(file__regex=GENERATED_NAME_REGEX)


def with_legacy_name(queryset):
    """Sounds whose file is still stored under a user-supplied name."""
    return queryset.exclude(file="").exclude(file__regex=GENERATED_NAME_REGEX)


def rename_to_generated_name(sound):
    """Write the new object, point the row at it, then drop the old one.

    The order matters. Interrupted between any two steps, the worst outcome is
    an orphaned object, never a row pointing at a key that no longer exists.

    Returns the new name. Raises OldFileNotRemoved when the rename itself
    worked but the old object could not be deleted; anything else raised means
    the sound is as it was.
    """
    old_name = sound.file.name
    storage = sound.file.storage
    with sound.file.open("rb") as handle:
        content = handle.read()

    # upload_to (sound_file_path) turns this into sounds/<uuid>.<ext>.
    sound.file.save(old_name.rsplit("/", 1)[-1], ContentFile(content), save=False)
    new_name = sound.file.name
    if not sound.file_name_original:
        sound.file_name_original = old_name.rsplit("/", 1)[-1]

    try:
        # Only these two columns: the instance was loaded before a possibly
        # long run, so a full save would write stale values over whatever
        # changed meanwhile (in_use is kept current with .update()), and would
        # re-insert a sound its owner deleted. With update_fields a missing row
        # raises instead; the savepoint keeps that failure from poisoning an
        # enclosing transaction, so the rest of a batch can go on.
        with transaction.atomic():
            sound.save(update_fields=["file", "file_name_original"])
    except Exception:
        sound.file.name = old_name
        _delete_quietly(storage, new_name)
        raise

    if old_name != new_name:
        try:
            storage.delete(old_name)
        except Exception as error:
            raise OldFileNotRemoved(old_name, new_name) from error
    return new_name


def _delete_quietly(storage, name):
    """Remove the copy made for a rename that did not go through."""
    try:
        storage.delete(name)
    except Exception:
        log.exception("Could not remove %s after a failed rename", name)
