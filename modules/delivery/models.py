# -*- coding: utf -*-

from django.db import models
from django.db.models.signals import post_save, post_delete

from datetime import datetime
from hashlib import md5

from delivery.utils import send_massmail


class SubscriberManager(models.Manager):
    """
    Easies access to objects by frequency
    """

    def get_daily(self):
        return self.filter(frequency=Subscriber.FREQUENCY_CHOICES[0][0])

    def get_weekly(self):
        return self.filter(frequency=Subscriber.FREQUENCY_CHOICES[1][0])

    def get_weekly_2(self):
        return self.filter(frequency=Subscriber.FREQUENCY_CHOICES[2][0])

    def get_monthly(self):
        return self.filter(frequency=Subscriber.FREQUENCY_CHOICES[3][0])



class Subscriber(models.Model):
    """
    Represents subscribers model
    """
    FREQUENCY_CHOICES = (
        ('daily', 'Щодня'),
        ('weekly', 'Раз на тиждень'),
        ('weekly_2', 'Раз на два тижні'),
        ('monthly', 'Раз на місяць'),
    )
    email = models.EmailField('Адреса ел. пошти', max_length=128, unique=True)
    is_subscribed = models.BooleanField('Підписаний', default=True)
    frequency = models.CharField('Періодичність', max_length=12,
                                choices=FREQUENCY_CHOICES)
    date = models.DateTimeField('Дата підписки', default=datetime.now(),
                               editable=False)
    hash = models.CharField('Унікальний хеш', blank=True,
                           max_length=128, editable=False)

    objects = SubscriberManager()

    class Meta:
        verbose_name = 'Підписчик'
        verbose_name_plural = 'Підписчики'

    def __unicode__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.hash = md5(str(self.date) + self.email).hexdigest()
        super(Subscriber, self).save(*args, **kwargs)
    
    @models.permalink
    def get_absolute_url(self):
        return ('delivery_detail', (),
                {'hash': self.hash, 'id': self.id})


class SubscribersMailSettings(models.Model):
    """
    Represents setting of the mail template to deliver
    """
    daily_title = models.CharField('Заголовок', max_length=256)
    daily_body = models.TextField('Повідомлення')
    daily_banner = models.TextField('Код баннеру', blank=True, null=True)
    weekly_title = models.CharField('Заголовок', max_length=256)
    weekly_body = models.TextField('Повідомлення')
    weekly_banner = models.TextField('Код баннеру', blank=True, null=True)
    weekly_2_title = models.CharField('Заголовок', max_length=256)
    weekly_2_body = models.TextField('Повідомлення')
    weekly_2_banner = models.TextField('Код баннеру', blank=True, null=True)
    monthly_title = models.CharField('Заголовок', max_length=256)
    monthly_body = models.TextField('Повідомлення')
    monthly_banner = models.TextField('Код баннеру', blank=True, null=True)
    happybirthday_title = models.CharField('Заголовок', max_length=256)
    happybirthday_body = models.TextField('Повідомлення')
    happybirthday_banner = models.TextField('Код баннеру', blank=True, null=True)

    class Meta:
        verbose_name = 'Налаштування розсилки'
        verbose_name_plural = 'Налаштування розсилок'
        get_latest_by = 'id'

    def __unicode__(self):
        return '%s / %s / %s / %s' % (self.daily_title, self.weekly_title,
                                         self.weekly_2_title, self.monthly_title)


class MassMail(models.Model):
    """
    Represents mail for sending via admin to all subscribed users
    """
    subject = models.CharField('Заголовок', max_length=256,
                               unique_for_date='date')
    body = models.TextField('Повідомлення')
    banner = models.TextField('Баннер', blank= True, null= True)
    date = models.DateTimeField('Дата відправки', default=datetime.now(),
                               editable=False)
    is_ready = models.BooleanField('Відправити?', default=True,
                                  help_text='Якщо зняти галочку,\
                                   повідомлення не буде відправлене.')
    
    class Meta:
        verbose_name = 'Массова розсилка'
        verbose_name_plural = 'Массові розсилки'
    
    def __unicode__(self):
        return self.subject


def remove_subscriber(sender, instance, **kwargs):
    if not instance.is_subscribed:
        instance.delete()

post_save.connect(remove_subscriber, sender=Subscriber)
post_save.connect(send_massmail, sender=MassMail)
