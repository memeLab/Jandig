


from django.db import models

class Calcartwork(models.Model,object):

   def __init__(self,work):   
      self.work=work        
         
   def exhibits_count(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__in=[self.work]).count()
    
   def exhibits_list(self):
        from core.models import Exhibit
        #artwork=Artwork.objects.get(id=self.id)
        return list(Exhibit.objects.filter(artworks__in=[self.work]))
