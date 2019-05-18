from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage

from .choices import COUNTRY_CHOICES


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)
    personal_site = models.URLField()

    #exhibits = ?
    #uploads = ?


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Marker(models.Model):
    source = models.ImageField(upload_to='markers/')
    author = models.CharField(max_length=60, blank=False)


class Object(models.Model):
    source = models.ImageField(upload_to='objects/')
    author = models.CharField(max_length=60, blank=False)


@receiver(post_delete, sender=Object)
@receiver(post_delete, sender=Marker)
def remove_source_file(sender, instance, **kwargs):
    instance.source.delete(False)
