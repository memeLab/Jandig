# Remove scales that are 0 and replace them with 1
# and round the rest to 2 decimals if not integer
# and remove trailing spaces if any
# and remove leading spaces if any
from django.db import migrations

def update_object_scale(apps, schema_editor):
    Object = apps.get_model('core', 'Object')
    for obj in Object.objects.all():
        scale_str = obj.scale
        if not scale_str:
            continue
        parts = scale_str.strip().split()
        new_parts = []
        for part in parts:
            try:
                num = float(part)
                if num == 0:
                    num = 1
                # Round to 2 decimals if not integer
                if num == int(num):
                    new_parts.append(str(int(num)))
                else:
                    new_parts.append(f"{num:.2f}")
            except ValueError:
                # If not a number, keep as is
                new_parts.append(part)
        new_scale = " ".join(new_parts)
        if new_scale != obj.scale:
            obj.scale = new_scale
            obj.save(update_fields=['scale'])

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_artwork_augmented_alter_artwork_marker'),
    ]

    operations = [
        migrations.RunPython(update_object_scale, reverse_code=migrations.RunPython.noop),
    ]


