from django.db import migrations


def populate_dimensions(apps, schema_editor):
    """Populate width/height for all existing Object records."""
    from core.media_dimensions import extract_dimensions

    Object = apps.get_model("core", "Object")
    objects_to_update = []

    for obj in Object.objects.filter(width__isnull=True):
        try:
            thumbnail = obj.thumbnail if obj.file_extension == "glb" else None
            source = obj.source
            if not source:
                continue
            with source.open("rb") as f:
                thumb_file = None
                if thumbnail:
                    try:
                        thumb_file = thumbnail.open("rb")
                    except Exception:
                        thumb_file = None

                dims = extract_dimensions(f, obj.file_extension, thumb_file)

                if thumb_file:
                    thumb_file.close()

            if dims:
                obj.width, obj.height = dims
                objects_to_update.append(obj)
        except Exception:
            continue

    if objects_to_update:
        Object.objects.bulk_update(objects_to_update, ["width", "height"], batch_size=100)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0035_object_width_height"),
    ]

    operations = [
        migrations.RunPython(populate_dimensions, migrations.RunPython.noop),
    ]
