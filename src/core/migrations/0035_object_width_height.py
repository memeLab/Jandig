from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0034_add_png_extension"),
    ]

    operations = [
        migrations.AddField(
            model_name="object",
            name="width",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="object",
            name="height",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
