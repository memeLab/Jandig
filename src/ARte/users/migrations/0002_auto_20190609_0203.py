# Generated by Django 2.2.1 on 2019-06-09 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='marker',
            name='uploaded_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='object',
            name='uploaded_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]