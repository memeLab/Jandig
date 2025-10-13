# PGHistory fields can't be null, because they follow what is in the original model.
# To keep track of ex-null values, we convert them to "None" string.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_add_thumbnail_field_to_objects'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectevent',
            name='file_extension',
            field=models.CharField(choices=[('gif', 'GIF'), ('mp4', 'MP4'), ('webm', 'WEBM'), ('glb', 'GLB')], default='None', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='objectevent',
            name='file_name_original',
            field=models.CharField(default='None', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='objectevent',
            name='file_size',
            field=models.IntegerField(default=0),
        ),
    ]
