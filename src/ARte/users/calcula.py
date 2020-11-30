


from django.db import models

class Calcartwork(models.Model,object):

   def __init__(self,work):   
      self.work=work        
         
   def exhibits_count_Artwrok(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__in=[self.work]).count()
    
   def exhibits_list_Artwork(self):
        from core.models import Exhibit
        return list(Exhibit.objects.filter(artworks__in=[self.work]))

   def exhibits_count_Object(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__augmented=self.work).count()
    
   def exhibits_list_Object(self):
        from core.models import Exhibit
        return list(Exhibit.objects.filter(artworks__augmented=self.work))
