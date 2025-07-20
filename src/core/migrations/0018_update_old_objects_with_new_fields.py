# Generate new fields for old Object models based on the old fields
# This migration ensures that the new fields are populated with the correct data
from django.db import migrations

def populate_file_names(apps, schema_editor):
    Object = apps.get_model('core', 'Object')
    for obj in Object.objects.all():
        filename = obj.source.name
        obj.file_name_original = filename.split('/')[-1] if filename else None
        Object.objects.filter(id=obj.id).update(file_name_original=obj.file_name_original)

def populate_file_extensions(apps, schema_editor):
    Object = apps.get_model('core', 'Object')
    for obj in Object.objects.all():
        obj.file_extension = obj.source.name.split('.')[-1] if obj.source.name else None
        Object.objects.filter(id=obj.id).update(file_extension=obj.file_extension)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_create_new_object_fields'),
    ]

    operations = [
        migrations.RunPython(populate_file_names, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(populate_file_extensions, reverse_code=migrations.RunPython.noop),
    ]
