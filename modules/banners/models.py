# -*- coding: utf-8 -*-
 
from django.db import models


class PlaceHolder(models.Model):
    """Placeholder which is displayed on the page"""
    title = models.CharField("Назва", max_length = 35)
    key = models.CharField("Унікальний-id", max_length = 20,unique = True, blank=True, help_text= "Латиницею будьласка")

    def __unicode__(self):
        return u"%s" % (self.title,)

    class Meta:
        verbose_name = u'Майданчик'
        verbose_name_plural = u'Майданчики розміщення'

class Banner(models.Model):
    """
    Banner instance, which is displayed in the Placeholder
    """
    title = models.CharField("Назва банера", max_length = 20, blank =True, null = True)
    key = models.CharField("Унікальний-id", max_length = 20,unique = True, blank=False, help_text= "Латиницею будьласка")
    content = models.TextField("Код Баннера", blank = True)
    holder = models.ForeignKey(PlaceHolder, verbose_name = "Контейнер, у якому показувати")
    ratio = models.PositiveSmallIntegerField("Частота ротації", help_text = "Пріорітет відображення банера (1-10)",  default = 5)

    def __unicode__(self):
        return u"%s" % (self.title,)

    class Meta:
        verbose_name = u'Банер'
        verbose_name_plural = u'Банери'
