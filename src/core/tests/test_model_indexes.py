from django.db import connection
from django.test import TestCase
from django_extensions.db.models import TimeStampedModel as UpstreamTimeStampedModel

from blog.models import Clipping, Post, PostImage
from core.models import Artwork, Exhibit, Marker, Object, Sound
from core.timestamps import TimeStampedModel

TIMESTAMPED = (Sound, Marker, Object, Artwork, Exhibit, Post, PostImage, Clipping)

COMPOSITE_INDEXES = {
    Exhibit: ("core_exhibit_type_created_idx", ["exhibit_type", "-created"]),
    Post: ("blog_post_status_created_idx", ["status", "-created"]),
}


class TestTimestampFieldsAreIndexed(TestCase):
    """Every listing sorts on created; the admin sorts on both columns."""

    def test_created_and_modified_are_indexed_on_every_model(self):
        for model in TIMESTAMPED:
            for field_name in ("created", "modified"):
                with self.subTest(model=model.__name__, field=field_name):
                    field = model._meta.get_field(field_name)
                    assert field.db_index is True, (
                        f"{model.__name__}.{field_name} is not indexed"
                    )

    def test_the_indexes_exist_in_the_database_schema(self):
        for model in TIMESTAMPED:
            with self.subTest(model=model.__name__):
                with connection.cursor() as cursor:
                    constraints = connection.introspection.get_constraints(
                        cursor, model._meta.db_table
                    )
                indexed = {
                    tuple(c["columns"]) for c in constraints.values() if c.get("index")
                }
                assert ("created",) in indexed, (
                    f"no index on {model._meta.db_table}.created; "
                    "the migration may not have been applied"
                )
                assert ("modified",) in indexed


class TestCompositeIndexes(TestCase):
    def test_filter_plus_sort_queries_get_a_composite_index(self):
        for model, (name, fields) in COMPOSITE_INDEXES.items():
            with self.subTest(model=model.__name__):
                declared = {index.name: index.fields for index in model._meta.indexes}
                assert declared.get(name) == fields


class TestTimestampBehaviourIsPreserved(TestCase):
    """Replacing the base class must not change what it did."""

    def test_models_no_longer_inherit_the_upstream_abstract_model(self):
        for model in TIMESTAMPED:
            with self.subTest(model=model.__name__):
                assert issubclass(model, TimeStampedModel)
                assert not issubclass(model, UpstreamTimeStampedModel)

    def test_get_latest_by_is_preserved(self):
        for model in TIMESTAMPED:
            with self.subTest(model=model.__name__):
                assert model._meta.get_latest_by == "modified"

    def test_saving_updates_modified(self):
        post = Post.objects.create(title="T", excerpt="E", formatted_body="B")
        first = post.modified

        post.title = "T2"
        post.save()

        assert post.modified > first

    def test_update_modified_false_keeps_the_timestamp(self):
        """The upstream save() flag has to keep working."""
        post = Post.objects.create(title="T", excerpt="E", formatted_body="B")
        first = post.modified

        post.title = "T2"
        post.save(update_modified=False)
        post.refresh_from_db()

        assert post.modified == first
