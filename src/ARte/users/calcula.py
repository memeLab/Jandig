


from django.db import models

class CalcExhibit(models.Model,object):

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

   def  artworks_list_Object(self):
        from .models import Artwork     
        return Artwork.objects.filter(augmented=self.work)

   def artworks_count_Object(self):
        from .models import Artwork   
        return Artwork.objects.filter(augmented=self.work).count()

   def in_use_Artwork(self):       
       if self.work.count>0:
          return True
       return False

   def in_use_Artwork_Exhibit(self): 
       if self.work.exhibits_count > 0 :  
           return True
       else:
          if self.work.artworks_count > 0 :
            return True         
       return False 
