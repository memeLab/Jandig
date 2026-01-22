from django.db import migrations, models

def populate_display_dates(apps, schema_editor):
    Clipping = apps.get_model('blog', 'Clipping')
    for obj in Clipping.objects.all():
        obj.display_date = obj.created
        obj.save()
        

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_alter_clipping_options_alter_post_options_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_display_dates, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='clipping',
            name='display_date',
            field=models.DateField(),
        ),
    ]
