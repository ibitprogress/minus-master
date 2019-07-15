# -*- coding: utf-8 -*-
from datetime import datetime
from pytils.translit import slugify

from django.utils.encoding import smart_unicode
from django.db import models
from django.db.models import permalink
from django.db.models.signals import post_save, post_delete, pre_save
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from djangoratings.fields import RatingField
 
def upload_filename(instance, filename):
    """
    Generates filenames for uploads
    """
    prefix = 'uploads/audio'
    uhash = abs(hash(u'%s%s' % (datetime.now(), filename)))
    user = instance.user.username

    dotindex = filename.find(".",-4,-1) #find dot, because it gets removed by slugify
    filename = slugify(filename[:dotindex])+filename[dotindex:] #preserve dot
    return u'%s/%s/%s_%s' % (prefix, user, uhash, filename)

class BaseAlbum(models.Model):
    """album attached to user
    Not using Album because of collisions
    """
    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType, null = True)
    object_pk = models.PositiveIntegerField(null = True)
    content_object = generic.GenericForeignKey('content_type', 'object_pk')

    name = models.CharField('Назва', max_length=128)
    slug = models.SlugField(unique=True)
    description = models.TextField('Опис', blank=True, null=True)
    pub_date = models.DateTimeField(auto_now_add = True,
                                       editable=False)

    class Meta:
        get_latest_by = 'pub_date',
        abstract = True

    def __unicode__(self):
        """"""
        return self.name

class BaseAlbumItem(models.Model):
    """
    Base abstract model for audios
    in future photo and video albums should be moved to this structure (TODO)
    """
    class Meta:
        abstract = True
        ordering = ('order','-pub_date',)

    user = models.ForeignKey(User)

    title = models.CharField('Заголовок', max_length=256, blank=True, null=True)
    description = models.TextField('Короткий опис', max_length=500, blank=True, null=True)
    pub_date = models.DateTimeField(default=datetime.now)
    order = models.IntegerField('Порядок', default = 0, 
        blank = False,
        help_text = 'У цьому порядку відображатимуться елементи'
        )

    def get_absolute_url(self):
        return self.user.get_profile().get_absolute_url()

    def __unicode__(self):
        return self.title

class AudioAlbum(BaseAlbum):
    """AudioAlbum"""
    pass

    @models.permalink
    def get_absolute_url(self):
        return ('show_album',['audio',self.user.username,self.slug])
        

class Audio(BaseAlbumItem):
    """
    Audios attached
    """
    album = models.ForeignKey(AudioAlbum,
        verbose_name = "Альбом", null = True, blank = True)
    file = models.FileField('Аудіозапис', max_length=256,
                              upload_to=upload_filename)
    downloadable = models.BooleanField('Дозволити скачування', 
        default = False)
    rating = RatingField('Рейтинг', range=5)



    @models.permalink
    def get_absolute_url(self):
        return ('show_object_detail', ['audio',
        self.user.username, self.album.slug, self.id])

    def __unicode__(self):
        if self.title:
            return self.title
        else:
            return self.file.name.split("/")[-1]

def create_album_for(instance=None, user=None, model = None, **kwargs):
    """
    Universal function for creating albums in different situations
    """
    if not user:
        user = instance.user

    ct = ContentType.objects.get_for_model(instance)
    album_name = u'Альбом %s' % smart_unicode(instance.__unicode__()) #had some issues
    slug = slugify(album_name+str(instance.id))
    album_dict = {
        'user': user,
        'name': album_name,
        'slug': slug,
        'content_type': ct,
        'object_pk': instance.pk,
        'description':u''
    }
    
    try:
        album = model.objects.get(content_type = ct, object_pk = instance.pk)
    except model.DoesNotExist:
        album = model.objects.create(**album_dict)
    return album

def audio_album(sender, instance, **kwargs):
    """docstring for audio_album"""
    if not instance.album:
        instance.album = create_album_for(instance.user,
        instance.user, model = AudioAlbum, **kwargs)
        instance.save()

def slugify_slug(sender, instance, **kwargs):
    instance.slug = slugify(smart_unicode(instance.name))

post_save.connect(audio_album, sender = Audio)
pre_save.connect(slugify_slug, sender = AudioAlbum)
