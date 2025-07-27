# Generate new fields for old Object models based on the old fields
# This migration ensures that the new fields are populated with the correct data
from django.db import migrations

def populate_artwork_scale_and_position(apps, schema_editor):
    Artwork = apps.get_model('core', 'Artwork')
    for artwork in Artwork.objects.all():
        augmented = artwork.augmented
        print(f"Processing artwork {artwork.id} with augmented {augmented.id}")
        print(f"Augmented position: {augmented.position}  scale: {augmented.scale}")

        x,y,_ = augmented.position.split(" ")
        print (f"Parsed position: x={x}, y={y}")
        scale_x, scale_y = augmented.scale.split(" ")
        print(f"Parsed scale: scale_x={scale_x}, scale_y={scale_y}")
        artwork.position_x = float(x)
        artwork.position_y = float(y)
        artwork.scale_x = float(scale_x)
        artwork.scale_y = float(scale_y)
        Artwork.objects.filter(id=artwork.id).update(
            position_x=artwork.position_x,
            position_y=artwork.position_y,
            scale_x=artwork.scale_x,
            scale_y=artwork.scale_y
        )
def populate_artwork_position_and_scale_with_defaults(apps, schema_editor):
    Artwork = apps.get_model('core', 'Artwork')
    for artwork in Artwork.objects.all():
        artwork.position_x = 0
        artwork.position_y = 0
        artwork.scale_x = 1.0
        artwork.scale_y = 1.0
        Artwork.objects.filter(id=artwork.id).update(
            position_x=artwork.position_x,
            position_y=artwork.position_y,
            scale_x=artwork.scale_x,
            scale_y=artwork.scale_y
        )

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_create_scale_and_position_on_artwork'),
    ]

    operations = [
        migrations.RunPython(populate_artwork_scale_and_position, reverse_code=populate_artwork_position_and_scale_with_defaults),

    ]
