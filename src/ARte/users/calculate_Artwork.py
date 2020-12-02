from django.db import models
from .models import Artwork
class CalcArtwork(models.Model):
    def __init__(self,work: Artwork):
       self.work=work

    def exhibits_count_Artwrok(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__in=[self.work]).count()

    def exhibits_list_Artwork(self):
        from core.models import Exhibit
        return list(Exhibit.objects.filter(artworks__in=[self.work]))

    def in_use_Artwork(self):
        if self.work.count>0:
            return True
        return False