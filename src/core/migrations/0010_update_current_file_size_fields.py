from django.db import migrations, models


def update_object_file_size(apps, schema_editor):
    Object = apps.get_model('core', 'Object')
    for obj in Object.objects.all():
        obj.file_size = obj.source.size
        obj.save()

def update_marker_file_size(apps, schema_editor):
    Marker = apps.get_model('core', 'Marker')
    for marker in Marker.objects.all():
        marker.file_size = marker.source.size
        marker.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_marker_file_size_object_file_size'),
    ]

    operations = [
        migrations.RunPython(update_object_file_size),
        migrations.RunPython(update_marker_file_size),
    ]

