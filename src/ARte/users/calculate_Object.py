from .models import Object
from core.models import Exhibit
from django.db import models
from .models import Artwork

class calcObject(models.Model):
    def __init__(self,work:Object):
        self.work=work

    def exhibits_count(self):
        return Exhibit.objects.filter(artworks__augmented=self.work).count()

    def exhibits_list(self):
        return list(Exhibit.objects.filter(artworks__augmented=self.work))

    def  artworks_list(self):
        return Artwork.objects.filter(augmented=self.work)

    def artworks_count(self):
        return Artwork.objects.filter(augmented=self.work).count()

    def in_use(self):
        if self.work.exhibits_count > 0 :
            return True
        else:
            if self.work.artworks_count > 0 :
                return True
        return False