from django.db import models
from users.models import Artwork, Profile
from datetime import datetime
import urllib


class Exhibit(models.Model):
    owner = models.ForeignKey(Profile,on_delete=models.DO_NOTHING,related_name="exhibits")
    name = models.CharField(unique=True, max_length=50)
    slug = models.CharField(unique=True, max_length=50)
    artworks = models.ManyToManyField(Artwork,related_name="exhibits")
    creation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def artworks_count(self):
        return self.artworks.count()

    @property
    def date(self):
        return self.creation_date.strftime("%d/%m/%Y")