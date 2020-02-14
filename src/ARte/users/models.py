from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
import re

from .choices import COUNTRY_CHOICES

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    bio = models.TextField(max_length=500, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)
    personal_site = models.URLField()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Marker(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    source = models.ImageField(upload_to='markers/')
    uploaded_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=60, blank=False)
    patt = models.FileField(upload_to='patts/')
    def __str__(self):
        return self.source.name

    @property
    def artworks_count(self):
        return Artwork.objects.filter(marker=self).count()

    @property
    def exhibits_count(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__marker=self).count()

    @property
    def in_use(self):
        if self.artworks_count > 0 or self.exhibits_count > 0:
            return True
        return False


class Object(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    source = models.FileField(upload_to='objects/')
    uploaded_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=60, blank=False)
    scale = models.CharField(default="1 1", max_length=50)
    position = models.CharField(default="0 0 0", max_length=50)
    rotation = models.CharField(default="270 0 0", max_length=50)
    def __str__(self):
        return self.source.name

    @property
    def artworks_count(self):
        return Artwork.objects.filter(augmented=self).count()

    @property
    def exhibits_count(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__augmented=self).count()

    @property
    def in_use(self):
        if self.artworks_count > 0 or self.exhibits_count > 0:
            return True

        return False
    
    @property
    def xproportion(self):
        a = re.findall(r'[\d\.\d]+', self.scale)
        width = float(a[0])
        height = float(a[1])
        if width > 1 :
            height = height*1.0/width
            width = 1
        elif height > 1 :
            width = width*1.0/height
            height = 1
        return width

    @property
    def yproportion(self):
        a = re.findall(r'[\d\.\d]+', self.scale)
        width = float(a[0])
        height = float(a[1])
        if width > 1 :
            height = height*1.0/width
            width = 1
        elif height > 1 :
            width = width*1.0/height
            height = 1
        return height

    @property
    def xscale(self):
        a = re.findall(r'[\d\.\d]+', self.scale)
        return a[0]

    @property
    def yscale(self):
        a = re.findall(r'[\d\.\d]+', self.scale)
        return a[1]

    @property
    def fullscale(self):
        x = self.xscale
        y = self.yscale
        if x > y:
            return x
        else:
            return y

    @property
    def xposition(self):
        a = re.findall(r'[\d\.\d]+', self.position)
        return a[0]

    @property
    def yposition(self):
        a = re.findall(r'[\d\.\d]+', self.position)
        return a[1]



@receiver(post_delete, sender=Object)
@receiver(post_delete, sender=Marker)
def remove_source_file(sender, instance, **kwargs):
    instance.source.delete(False)


class Artwork(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    marker = models.ForeignKey(Marker, on_delete=models.DO_NOTHING)
    augmented = models.ForeignKey(Object, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=50, blank=False)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    @property
    def exhibits_count(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__in=[self]).count()

    @property
    def in_use(self):
        if self.exhibits_count > 0:
            return True

        return False
