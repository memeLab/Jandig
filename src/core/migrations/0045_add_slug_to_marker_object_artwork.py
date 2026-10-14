# Renumbered from 0028 when develop was merged in: two 0028_* migrations
# would leave the graph with conflicting leaf nodes.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0044_populate_sound_in_use_fields"),
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
