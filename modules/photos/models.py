# -*- coding:utf-8 -*-

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse

from datetime import datetime
import re
import os

from photos.utils import image_upload_filename, image_optimize
from photos.managers import AlbumManager
from albums.models import BaseAlbum, create_album_for


class PhotoAlbum(BaseAlbum):
    size = models.IntegerField('Розмір фотоальбому', default=0)
    objects = models.Manager()
    albums = AlbumManager()

    
    def __unicode__(self):
        return self.user.get_profile().fullname()

    def get_cover_photo(self):
        if self.photo_set.filter(is_cover=True).count() > 0:
            return self.photo_set.filter(is_cover=True)[0]
        elif self.photo_set.all().count() > 0:
            return self.photo_set.all()[0]
        else:
            return None


    def get_absolute_url(self):
        return reverse('album_detail', args=[self.slug])


class Photo(models.Model):
    title = models.CharField('Заголовок', max_length=256, blank=True)
    description = models.TextField('Опис', blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.now)
    image = models.ImageField('Зображення', max_length=256,
                              upload_to=image_upload_filename)
    album = models.ForeignKey(PhotoAlbum, verbose_name='Фотоальбом')
    is_cover = models.BooleanField('Обкладинка', default=False)

    class Meta:
        get_latest_by = 'date_created'
        ordering = ['-date_created']
    
    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.image.name.rsplit('/')[-1]
        super(Photo, self).save(*args, **kwargs)

    def get_thumbnail(self):
        thumbnail = re.sub(r'(.+)(\.[^.]*)','\\1'\
                           + settings.PHOTO_THUMB_SUFFIX + '\\2',
                           self.image.path)
        return thumbnail

    def get_thumbnail_url(self):
        thumbnail_url = re.sub(r'(.+)(\.[^.]*)','\\1'\
                               + settings.PHOTO_THUMB_SUFFIX + '\\2',
                               self.image.url)
        return thumbnail_url

    def get_absolute_url(self):
        return reverse('photo_detail', args=[self.album.slug,
                                            self.id])

    def delete(self):
        # Update album size
        album = self.album
        album.size -= self.image.size
        album.save()
        # Remove thumbnail file
        thumbnail = self.get_thumbnail()
        try:
            os.remove(thumbnail)
        except:
            pass
        super(Photo, self).delete()
        


def process_image(sender, instance, **kwargs):
    if instance.image:
        image_thumbnail_processed = image_optimize(instance.image.path,
                                    settings.PHOTO_THUMB_WIDTH,
                                    settings.PHOTO_THUMB_HEIGHT, True)
        image_thumbnail = re.sub(r'(.+)(\.[^.]*)','\\1'\
                                 + settings.PHOTO_THUMB_SUFFIX + '\\2',
                                 instance.image.path)
        image_thumbnail_processed.save(image_thumbnail, 'JPEG')

        image_processed = image_optimize(instance.image.path,
                                         settings.PHOTO_WIDTH,
                                         settings.PHOTO_HEIGHT, False)
        image_processed.save(instance.image.path, 'JPEG')
        
def update_album_size(sender, instance, **kwargs):
    album = instance.album
    album.size += instance.image.size
    album.save()



def create_photo_album(sender, instance, **kwargs):
    """sender should be userprofile"""
    create_album_for(instance, instance.user, model = PhotoAlbum, **kwargs)
    

post_save.connect(process_image, sender=Photo)
post_save.connect(update_album_size, sender=Photo)
