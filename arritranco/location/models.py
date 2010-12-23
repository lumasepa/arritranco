from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.
class Building(models.Model):
    """
        A model to represent a simple Building
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    map_location = models.ImageField(upload_to=_("buildings_map"), blank=True)
    area = models.IntegerField(choices = settings.AREA_CHOICES)
    campo = models.CharField(max_length=200)


    def __unicode__(self):
        return u'%s' % (self.name, )


class Floor(models.Model):
    """
        A model to represent a floor in a building
    """
    name = models.CharField(max_length = 255, blank = True, null=True)
    slug = models.SlugField()
    number = models.IntegerField()
    building = models.ForeignKey(Building)

    def __unicode__(self):
        return u'%s (%s)' % (self.name , self.building.name)

class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    floor = models.ForeignKey(Floor)
    location = models.TextField(blank=True, null=True,
        help_text=u'Text to describe the way to the room')
    #TODO: We may need to include a photologue gallery here

    def __unicode__(self):
        return u'%s (%s - %s)' % (self.name ,self.floor.building.name, self.floor.name)

class Place(models.Model):
    room = models.ForeignKey(Room)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank = True, null = True,
        help_text = u"A description of the place inside the room")