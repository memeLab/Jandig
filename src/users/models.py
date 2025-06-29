from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .choices import COUNTRY_CHOICES


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(max_length=500, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)
    personal_site = models.URLField()

    def __str__(self):
        return str(self.id)

    @property
    def artworks_count(self):
        """Count of artworks by the user"""
        return self.artworks.count()

    @property
    def markers_count(self):
        """Count of markers by the user"""
        return self.markers.count()

    @property
    def ar_objects_count(self):
        """Count of AR objects by the user"""
        return self.ar_objects.count()

    @property
    def exhibits_count(self):
        """Count of exhibits by the user"""
        return self.exhibits.count()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
