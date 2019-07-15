# -*- coding: utf-8 -*-
import pytils, os
from django.db import models 
from django.conf import settings
from django.core.files.storage import FileSystemStorage

def up_radio_filename(instance, filename):
    prefix = u'radio/'
    if isinstance(instance, RadioJingle):
        prefix += u'jingles/'
    basename,extension = os.path.splitext(filename.split('/')[-1])
    filename = pytils.translit.slugify(basename)+extension #make safe filename
    return u'%s%s' % (prefix, filename)
        
class RadioPlaylist(models.Model):
    title = models.CharField(u"Назва плейліста", max_length = 30)
    play_date = models.DateField("Дата відтворення", blank = True, null = True)
    play_time = models.TimeField("Час відтворення", blank = True, null = True,
        help_text = "Якщо не вказувати дату, гратиме щодня")

class RadioJingle(models.Model):
    title = models.CharField(u"Назва", max_length = 30)
    file = models.FileField(u"Файл", max_length = 2048,
        upload_to = up_radio_filename,
        storage = FileSystemStorage(location = settings.STORAGE_ROOT))
    enabled = models.BooleanField("Використовується", default = True)

    def __unicode__(self):
        return self.title

class RadioSong(RadioJingle):
    playlist = models.ManyToManyField(RadioPlaylist,
        verbose_name = "Належить до плейліста",
        null = True, blank = True, related_name = 'songs')
    
