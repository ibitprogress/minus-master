# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save

from datetime import datetime
from links.utils import send_notification


class FriendLinkManager(models.Manager):

    def get_approved(self):
        """
        Represents objects list with only approved banners
        """
        return self.filter(is_approved=True)


class FriendLinkCategory(models.Model):
    """
    Represents categoris for friend links
    """
    name = models.CharField('Назва категорії', max_length=256)

    class Meta:
        ordering = ['name']
        verbose_name = 'Розділ сайтів-друзів'
        verbose_name_plural = 'Розділи сайтів-друзів'

    def __unicode__(self):
        return self.name


class FriendLink(models.Model):
    """
    Represents banners and friend links which are moderated
    """
    title = models.CharField('Назва сайту', max_length=256)
    site = models.URLField('Адреса сайту', verify_exists=True,
                          max_length=256)
    category = models.ForeignKey(FriendLinkCategory,
                                 verbose_name='Розділ')
    description = models.TextField('Короткий опис сайту')
    image_code = models.TextField('Код графічної кнопки', blank=True,
                                 null=True)
    banner_page = models.URLField('Адреса сторінки де буде розміщено наш\
                                   банер', verify_exists=False,
                                 max_length=512, blank=True, null=True)
    email = models.EmailField('Контактний E-Mail', max_length=128)
    is_approved = models.BooleanField('Підтвердити', default=False)
    date_created = models.DateTimeField('Створено', default=datetime.now)
    date_approved = models.DateTimeField('Підтвердженно', auto_now=True)
    # Becomes True when banner owner has been notified
    is_notified = models.BooleanField('Власник баннеру отпримав повідомлення про\
                                      розміщення його коду на сайті',
                                     default=False)

    objects = FriendLinkManager()

    class Meta:
        ordering = ['-date_approved']
        verbose_name = 'Сайт-друг'
        verbose_name_plural = 'Сайти-друзі'

    def __unicode__(self):
        return '%s: %s' % (self.title, self.description)


def notice_site_owner(sender, instance, **kwargs):
    """
    Sends mail notification to site owner when new link with banner
    has been submitted
    """
    if not kwargs['created']:
        return

    send_notification(instance)

def notice_banner_owner(sender, instance, **kwargs):
    """
    Sends mail notification to banner owner when it is approved
    """
    if not instance.is_approved or instance.is_notified:
        return

    send_notification(instance, template='links/banner_owner_notice.html',
                     recipient=[instance.email,])
    if not instance.is_notified:
        instance.is_notified = True
        instance.save()


post_save.connect(notice_site_owner, sender=FriendLink)
post_save.connect(notice_banner_owner, sender=FriendLink)
