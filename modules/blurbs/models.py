# -*- coding: utf-8 -*-
import pytils
import datetime
from django.db import models
from django.utils.encoding import smart_unicode
from photos.models import create_photo_album


class BlurbCategory(models.Model):
    """Category to sort blurbs"""
    title = models.CharField("Категорія",max_length = 60)
    slug = models.SlugField(max_length = 60,
        blank = True, 
        editable = False)
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = u'Категорія'
        verbose_name_plural = u'Категорії'
        ordering = ('title',)



def slugify_slug(sender,instance, *args, **kwargs):
    if instance.title:
        instance.slug = pytils.translit.slugify(smart_unicode(instance.title))
    
class GeoRegion(models.Model):
    title = models.CharField("Область", max_length = 30)

    def __unicode__(self):
        return self.title

class GeoCity(models.Model):
    title = models.CharField("Місто", max_length = 30)
    region = models.ForeignKey(GeoRegion)
    is_city = models.BooleanField(default = False)
    
    def __unicode__(self):
        return self.title


BUYSELL_CHOICES = (('B',u'Куплю'), ('S',u'Продам'))

class Blurb(models.Model):
    title = models.CharField("Назва товару", max_length = 120)
    description = models.TextField("Опис товару",
        max_length = 1000, blank = True)

    buysell = models.CharField("Куплю/продам",
        max_length = 1,
        choices = BUYSELL_CHOICES,
        )
    user = models.ForeignKey('auth.User')
    
    georegion = models.ForeignKey(GeoRegion, verbose_name = "Область",
        blank = True, null = True)

    geocity = models.ForeignKey(GeoCity, verbose_name = "Місто",
        blank = True, null = True)

    category = models.ForeignKey(BlurbCategory, verbose_name = "Категорія",
        help_text = "Виберіть серед наявних",
        blank = True)
    pub_date = models.DateTimeField(auto_now_add = True, editable = True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = u'Оголошення'

    def is_week_ago(self):
        return self.pub_date < datetime.datetime.now() - datetime.timedelta(days = 7)
        
    @models.permalink
    def get_absolute_url(self):
        return ('blurb_detail', [self.category.slug, self.buysell, str(self.id)])

def set_region(sender, instance, *args, **kwargs):
    """set region if no city specified"""
    if instance.geocity and not instance.georegion:
        instance.georegion = instance.geocity.region

models.signals.pre_save.connect(slugify_slug, sender = BlurbCategory)
models.signals.post_save.connect(create_photo_album, sender=Blurb)
models.signals.pre_save.connect(set_region, sender=Blurb)
