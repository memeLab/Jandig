# Generated manually to add slug fields to Marker, Object, and Artwork models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_sound_soundevent_remove_artwork_insert_insert_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='marker',
            name='slug',
            field=models.SlugField(blank=True, max_length=80, unique=True),
        ),
        migrations.AddField(
            model_name='object',
            name='slug',
            field=models.SlugField(blank=True, max_length=80, unique=True),
        ),
        migrations.AddField(
            model_name='artwork',
            name='slug',
            field=models.SlugField(blank=True, max_length=80, unique=True),
        ),
    ]
