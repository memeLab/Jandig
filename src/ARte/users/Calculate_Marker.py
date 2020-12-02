from .models import Marker
from core.models import Exhibit
from .models import Artwork
from django.db import models

class calcMarker(models.Model):
    def __init__(self,work:Marker):
        self.work=work

    def exhibits_count(self):
        return Exhibit.objects.filter(artworks__marker=self.work).count()

    def exhibits_list(self):
        return list(Exhibit.objects.filter(artworks__marker=self.work))

    def  artworks_list(self):
        return Artwork.objects.filter(marker=self.work)

    def artworks_count(self):
        return Artwork.objects.filter(marker=self.work).count()

    def in_use(self):
        if self.work.exhibits_count > 0 :
            return True
        else:
            if self.work.artworks_count > 0 :
                return True
        return False