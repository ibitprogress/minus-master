# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, post_delete

from datetime import datetime

from videos.managers import VideoAlbumManager


class VideoAlbum(models.Model):
    user = models.ForeignKey(User, unique=True,
                            verbose_name='Користувач')
    name = models.CharField('Назва', max_length=128)
    slug = models.SlugField(unique=True)
    description = models.TextField('Опис', blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.now,
                                       editable=False)
    videos_count = models.IntegerField('Кількість відеокліпів', default=0)
    objects = models.Manager()
    video_albums = VideoAlbumManager()

    class Meta:
        get_latest_by = 'date_created',
    
    def __unicode__(self):
        return self.user.get_profile().fullname()

    def get_absolute_url(self):
        return reverse('video_album_detail', args=[self.slug])


class Video(models.Model):
    title = models.CharField('Заголовок', max_length=256, blank=False, null=False)
    description = models.TextField('Опис', blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.now)
    embed_video = models.TextField("Відео",
                                    help_text = u'Підтримувані сервіси: youtube',
                                  blank=False, null=False)
    video_album = models.ForeignKey(VideoAlbum, verbose_name='Відеоальбом')

    class Meta:
        get_latest_by = 'date_created'
        ordering = ['-date_created']

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('video_detail', args=[self.video_album.slug,
                                            self.id])

def update_videos_count(sender, instance, **kwargs):
    video_album = instance.video_album
    video_album.videos_count = Video.objects.count()
    video_album.save()

post_save.connect(update_videos_count, sender=Video)
post_delete.connect(update_videos_count, sender=Video)
