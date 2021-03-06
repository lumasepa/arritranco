# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class Campus(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    def __unicode__(self):
        return self.name


class Building(models.Model):
    """
        A model to represent a simple Building
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    map_location = models.ImageField(upload_to=_("buildings_map"), blank=True)
    area = models.IntegerField(choices=settings.AREA_CHOICES)
    campus = models.ForeignKey(Campus)

    def __unicode__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=255)
    building = models.ForeignKey(Building)
    floor = models.IntegerField()
    location = models.TextField(blank=True, null=True,
                                help_text=_(u'Text to describe the way to the room'))
    slug = models.SlugField()
    #TODO: We may need to include a photologue gallery here

    def __unicode__(self):
        return u'%s (%s)' % (self.name , self.building.name)

    def rack_set_order(self):
        return self.qsort(self.rack_set.all())

    def qsort(self, list):
        if not list:
            return []
        else:
            pivot = list[0]
            lesser = self.qsort([x for x in list[1:] if x.get_index() < pivot.get_index()])
            greater = self.qsort([x for x in list[1:] if x.get_index() >= pivot.get_index()])
            return lesser + [pivot] + greater
