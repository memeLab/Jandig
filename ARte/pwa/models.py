from django.db import models

class Marker(models.Model):
    name = models.CharField(unique=True, max_length=50)
    scale = models.CharField(default="1 1", max_length=50)
    position = models.CharField(default="0 0 0", max_length=50)
    patt = models.CharField(default="hiro", max_length=50)
    gif = models.CharField(default="peixe", max_length=50)
    rotation = models.CharField(default="270 0 0", max_length=50)