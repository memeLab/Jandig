# Generated by Django 2.2.10 on 2020-12-02 22:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20201202_2230'),
        ('users', '0007_auto_20200220_1425'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='marker',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='object',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Artwork',
        ),
        migrations.DeleteModel(
            name='Marker',
        ),
        migrations.DeleteModel(
            name='Object',
        ),
    ]