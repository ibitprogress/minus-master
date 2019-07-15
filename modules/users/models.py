# -*- coding: utf-8 -*-
from math import sqrt

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.contenttypes import generic
from django.conf import settings
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.template.loader import render_to_string

import os

import datetime

from videos.models import VideoAlbum
from voting.models import Vote
from minusstore.models import MinusRecord
from users.utils import avatar_upload_filename, avatar_optimize


class UserProfile(models.Model):
    """
    Represent user profile for User object,
    accesible by get_profile() method
    """
    GENDER_CHOICES = (
        ('male', 'Чоловіча'),
        ('female', 'Жіноча'),
    )
    user = models.ForeignKey(User, unique=True, verbose_name='Користувач')
    gender = models.CharField('Стать', max_length=6, choices=GENDER_CHOICES,
                             blank=True, null=True)
    city = models.CharField('Місто', max_length=128, blank=True, null=True)
    country = models.CharField('Країна', max_length=128, blank=True, null=True)
    avatar = models.ImageField('Аватар', max_length=128, blank=True, null=True,
                              upload_to=avatar_upload_filename)
    birthdate = models.DateField('Дата Народження', blank=True, null=True)
    hide_birthdate = models.BooleanField('Приховати дату народження',
                                             default=False)
    icq = models.CharField('ICQ', max_length=10, blank=True, null=True)
    jabber = models.EmailField('Jabber', max_length=128, blank=True, null=True)
    skype = models.CharField('Skype', max_length=128, blank=True, null=True)
    website = models.URLField('Вебсайт', verify_exists=False, max_length=128,
                             blank=True, null=True)
    about = models.TextField('Про себе', blank=True, null=True)
    #Subscribe users to mass mail
    is_admin_subscribed = models.BooleanField('Отримувати листи від адміністрації',
                                              default=True)
    status_title = models.CharField('Статуc користувача', max_length = 20, 
        blank = True, null = True, default = "Користувач")
    status_css = models.CharField('CSS-стиль для статусу', max_length = 20, 
        blank = True, null = True, default = "")

    banned = models.BooleanField('Користувача забанено', default = False)
    banned_until = models.DateField(default = datetime.date.today()\
        +datetime.timedelta(days = 30), blank = True, null = True) 

    seen_rules = models.BooleanField('Ознайомився з правилами', default= False)
    
    # methods added for backwards compability
    def name(self):
        return self.user.first_name
    def surname(self):
        return self.user.last_name
    ###

    class Meta:
        db_table = 'userprofile'
        verbose_name = 'Профіль користувача'
        verbose_name_plural = 'Профілі користувачів'
        ordering = ['-id']
        get_latest_by = 'id'

    def __unicode__(self):
        return self.fullname()

    def get_album_slug(self):
        return self.user.photoalbum_set.select_related().get().slug

    def has_photos(self):
        """helper to find out, does user have any photos
        
        in newer implementation, it's not necessary for user to have
        album
        """
        return self.user.photoalbum_set.filter(object_pk = self.id).exists()

    def has_videos(self):
        return bool(self.user.videoalbum_set.all()[0].video_set.all())



    @models.permalink
    def get_absolute_url(self):
        return ('user_profile', [self.user.username])

    def fullname(self):
        if self.user.first_name or self.user.last_name:
            return "%s %s" % (self.user.first_name, self.user.last_name)
        else:
            return self.user.username

    def is_versed(self):
        if self.user.date_joined < (datetime.datetime.today()\
            - datetime.timedelta(days = 30)): return True
        else: return False

    def small_avatar_url(self):
        if self.avatar:
            path,ext = os.path.splitext(self.avatar.url)
            return path+'small'+ext
        else:
            return settings.MEDIA_URL+'avatars/default_small.png'
        

class UserRating(models.Model):
    """Advanced combined ratings model"""
    user = models.OneToOneField(User, unique=True,
        verbose_name='Користувач', related_name = 'u_rate')
    rating = models.IntegerField('Просунутий рейтинг',
        editable = False, default = 0, null = False, blank = False)
    average_minus_rating = models.IntegerField('Середній рейтинг файлів',
        editable = False, default = 0, null = False, blank = False)

    def count_rating(self):
        minuses = MinusRecord.objects.filter(user = self.user)
        count = minuses.count()
        if count != 0:
            sum = minuses.aggregate(models.Sum('rating_score'))['rating_score__sum']
            self.average_minus_rating = sum/count #arifmethic middle #cheaper
            #than using Avg
            self.rating = int(10*(sqrt(sum)+Vote.objects.get_score(self.user)['score']))
            self.save()



class UserActivity(models.Model):
    """
    Represents user's last activity to generate users online list
    """
    last_activity_ip = models.IPAddressField()
    last_activity_date = models.DateTimeField(\
        default = datetime.datetime(1950, 1, 1))
    user = models.OneToOneField(User, primary_key=True)

    class Meta:
        verbose_name = 'Активність користувачів'
        verbose_name_plural = 'Активність користувачів'
        ordering = ['-last_activity_date']
        get_latest_by = 'last_activity_date'

    def __unicode__(self):
        return self.user.get_profile().fullname()
    

class StaffTicket(models.Model):
    """tickets from users to moderators about some problems on site"""
    user = models.ForeignKey(User, verbose_name = "Користувач")
    content_type = models.ForeignKey(ContentType, verbose_name = "Тип об’єкту")
    object_id = models.PositiveIntegerField("ID об’єкту")
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    url = models.URLField(verify_exists = False,
        blank = True, null = True)
    message = models.TextField("Повідомлення",blank = True, null = True)
    pub_date = models.DateTimeField("Додано",auto_now_add = True)
    is_done = models.BooleanField("Виконано", default = False)

    class Meta:
        verbose_name = u'Заявка'
        verbose_name_plural = u'Заявки до модераторів'
        ordering = ['is_done','-pub_date']

    def __unicode__(self):
        return u"До об’єкту %s, від %s" % (self.content_object, self.user.get_profile().fullname())


def manage_userprofile(sender, instance=None, **kwargs):
    """
    Creates profile beside User object creation
    """
    if instance is None:
        return
    userprofile, created = UserProfile.objects.get_or_create(user=instance)

def check_banned(sender, instance=None, **kwargs):
    """"""
    if instance.banned:
        [s.delete() for s in Session.objects.all() if\
            s.get_decoded().get('_auth_user_id') == instance.user.id]




def create_rating(sender, instance=None, **kwargs):
    """
    Creates rating after user object creation
    """
    if instance is None:
        return
    rating, created = UserRating.objects.get_or_create(user=instance)
    rating.count_rating()
    rating.save()

def create_user_video_album(sender, instance=None, **kwargs):
    """
    Creates video album when user is activate
    """
    if instance is None:
        return

    video_album_dict = {
        'user': instance,
        'name': u'Відеоальбом користувача %s' % instance.get_profile().fullname(),
        'slug': instance.username,
    }
    try:
        VideoAlbum.objects.get(user = instance)
    except VideoAlbum.DoesNotExist:
        VideoAlbum.objects.create(**video_album_dict)

def process_avatar(sender, instance, **kwargs):
    if instance.avatar:
        
        path,ext = os.path.splitext(instance.avatar.path)
        avatar_processed = avatar_optimize(instance.avatar.path,
                                           settings.AVATAR_WIDTH,
                                           settings.AVATAR_HEIGHT,
                                           True)

        small_avatar_processed = avatar_optimize(instance.avatar.path,
                                           settings.AVATAR_SMALL_WIDTH,
                                           settings.AVATAR_SMALL_HEIGHT,
                                           True)

        os.rename(path+ext, path+'orig'+ext)
        small_avatar_processed.save(path+"small"+ext, 'JPEG')
        avatar_processed.save(instance.avatar.path, 'JPEG')

def check_for_abuse(sender, instance, **kwargs):
    """ instance auth.models.User"""
    if instance.first_name and instance.last_name:
        same_names_qs = User.objects.filter(first_name = instance.first_name,
            last_name = instance.last_name)
        if same_names_qs.count() > 1:
            # one is our actual record
            # using post-save, because having existing 
            # instance with names prevents us from
            # duplicating calls on each save
            ct = ContentType.objects.get_for_model(User)
            # now check didnt we notify staff already?
            if not StaffTicket.objects.filter(content_type = ct,
                object_id = instance.id).exists():

                other_users_qs = same_names_qs.exclude(id = instance.id)
                default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
                current_domain = Site.objects.get_current().domain
                message = render_to_string('users/staff_names_match_msg.txt', {
                    'site_url': '%s://%s' % (default_protocol, current_domain),
                    'user': instance,
                    'other_users_qs': other_users_qs,
                })

                st = StaffTicket.objects.create(user = instance,
                    content_type = ct,
                    object_id = instance.id,
                    url = instance.get_profile().get_absolute_url(),
                    message = message)
                st.save()



            


post_save.connect(manage_userprofile, sender=User)
post_save.connect(check_for_abuse, sender=User)
post_save.connect(check_banned, sender=UserProfile)
post_save.connect(create_rating, sender=User)
post_save.connect(create_user_video_album, sender=User)
post_save.connect(process_avatar, sender=UserProfile)

