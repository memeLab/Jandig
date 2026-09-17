"""Project-local replacement for django-extensions' TimeStampedModel.

`django_extensions.db.models.TimeStampedModel` declares `created` and
`modified` without indexes, and the models here sort and filter on them
constantly (every listing orders by `-created`; the admin sorts on both).
Adding `Meta.indexes` to every concrete model would work, but it leaves us
declaring indexes for fields we do not own — so the fields are declared here
instead, and the index lives on the field where it belongs.

The `django-extensions` dependency is deliberately kept: the same field
classes are reused, so historical migrations that reference
`django_extensions.db.fields.*` keep resolving on a fresh environment
without squashing.

Behaviour is identical to the upstream class, including the `update_modified`
save flag honoured by `ModificationDateTimeField.pre_save`.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import (
    CreationDateTimeField,
    ModificationDateTimeField,
)


class TimeStampedModel(models.Model):
    """Self-managed, indexed `created` and `modified` timestamps."""

    created = CreationDateTimeField(_("created"), db_index=True)
    modified = ModificationDateTimeField(_("modified"), db_index=True)

    def save(self, **kwargs):
        self.update_modified = kwargs.pop(
            "update_modified", getattr(self, "update_modified", True)
        )
        super().save(**kwargs)

    class Meta:
        get_latest_by = "modified"
        abstract = True
