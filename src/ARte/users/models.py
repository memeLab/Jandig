from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from django.core.files.base import ContentFile
from io import BytesIO, StringIO
from PIL import Image
from pymarker.core import generate_marker, generate_patt

import re

from .choices import COUNTRY_CHOICES

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    bio = models.TextField(max_length=500, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)
    personal_site = models.URLField()

    def __str__(self):
        return str(self.user)

    class Meta:
        permissions = [
            ("moderator", "Can moderate content"),
        ]

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if  created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
