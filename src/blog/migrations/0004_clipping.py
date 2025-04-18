# Generated by Django 4.1.5 on 2024-06-23 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0003_alter_post_created_alter_postimage_file"),
    ]

    operations = [
        migrations.CreateModel(
            name="Clipping",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=200)),
                ("description", models.CharField(max_length=500)),
                ("link", models.URLField()),
                ("file", models.FileField(upload_to="")),
                ("created", models.DateTimeField()),
                ("updated", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
