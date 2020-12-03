from django.db import models
from users.models import Profile
from datetime import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import urllib
import re 

class Marker(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)
    source = models.ImageField(upload_to='markers/')
    uploaded_at = models.DateTimeField(auto_now=True)
    author = models.CharField(max_length=60, blank=False)
    title = models.CharField(max_length=60, default='')
    patt = models.FileField(upload_to='patts/')

    def __str__(self):
        return self.source.name

    @property
    def artworks_count(self):
        return Artwork.objects.filter(marker=self).count()

    @property
    def artworks_list(self):
        return Artwork.objects.filter(marker=self)

    @property
    def exhibits_count(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__marker=self).count()

    @property
    def exhibits_list(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__marker=self)

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
    title = models.CharField(max_length=60, default='')
    scale = models.CharField(default="1 1", max_length=50)
    position = models.CharField(default="0 0 0", max_length=50)
    rotation = models.CharField(default="270 0 0", max_length=50)

    def __str__(self):
        return self.source.name

    @property
    def artworks_count(self):
        return Artwork.objects.filter(augmented=self).count()

    @property
    def artworks_list(self):
        return Artwork.objects.filter(augmented=self)

    @property
    def exhibits_count(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__augmented=self).count()

    @property
    def exhibits_list(self):
        from core.models import Exhibit
        return Exhibit.objects.filter(artworks__augmented=self)

    @property
    def in_use(self):
        if self.artworks_count > 0 or self.exhibits_count > 0:
            return True

        return False
    
    @property
    def xproportion(self):
        '''
        The 'xproportion' method is used to always reduce scale
        to 1:[something], so that new calculations can be made 
        when a new scale value is entered by the user.
        '''
        a = re.findall(r'[\d\.\d]+', self.scale)
        width = float(a[0])
        height = float(a[1])
        if width > height :
            height = (height*1.0)/width
            width = 1
        else :
            width = (width*1.0)/height
            height = 1
        return width

    @property
    def yproportion(self):
        '''
        The 'yproportion' method is used to always reduce scale
        to 1:[something], so that new calculations can be made 
        when a new scale value is entered by the user.
        '''
        a = re.findall(r'[\d\.\d]+', self.scale)
        width = float(a[0])
        height = float(a[1])
        if width > height :
            height = (height*1.0)/width
            width = 1
        else :
            width = (width*1.0)/height
            height = 1
        return height

    @property
    def xscale(self):
        '''
        The 'xscale' method returns the original proportion
        of the Object multiplied by the scale value entered
        by the user, and thus the Object appears resized in
        augmented reality.
        '''
        a = re.findall(r'[\d\.\d]+', self.scale)
        return a[0]

    @property
    def yscale(self):
        '''
        The 'yscale' method returns the original proportion
        of the Object multiplied by the scale value entered
        by the user, and thus the Object appears resized in
        augmented reality.
        '''
        a = re.findall(r'[\d\.\d]+', self.scale)
        return a[1]

    @property
    def fullscale(self):
        '''
        The 'fullscale' method is a workaround to show the
        users the last scale value entered by them, when
        they attempt to edit it.
        '''
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
    def exhibits_list(self):
        from core.models import Exhibit
        return list(Exhibit.objects.filter(artworks__in=[self]))
    
    @property
    def in_use(self):
        if self.exhibits_count > 0:
            return True

        return False

@receiver(post_delete, sender=Object)
@receiver(post_delete, sender=Marker)
def remove_source_file(sender, instance, **kwargs):
    instance.source.delete(False)

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
