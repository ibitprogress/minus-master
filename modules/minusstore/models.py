# -*- coding: utf-8 -*-
import datetime

from django.db.models import permalink
from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


from djangoratings.fields import RatingField

from minusstore.utils import up_filename, audio_storage

class FileType(models.Model):
    """
    model that divides records by types:
    Example: audio, midi, text
    """
    type_name = models.CharField("Назва типу файлів", max_length = 15)
    display_name = models.CharField("Назва що відображатиметься на сайті",
            max_length = 20, blank = True, null = True)
    description = models.TextField("Опис", null = True, blank = True)
    filetype = models.CharField(help_text=\
            u"Введіть розширення файлів через кому (mp3,wav)",
            max_length = 30)

    def __unicode__(self):
        if self.display_name:
            return self.display_name
        else:
            return self.type_name

    class Meta:
        verbose_name = 'тип'
        verbose_name_plural = 'Типи файлів'
        ordering = ['type_name']

class MinusCategory(models.Model):
    """
    Model that divides minuses by categories (greetings, for children, etc)
    """
    name = models.CharField("Категорія",max_length = 15)
    display_name = models.CharField("Відображувана назва категорії",
        max_length = 20, blank = True, null = True)
    def __unicode__(self):
        if self.display_name:
            return self.display_name
        else:
            return self.name

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії записів'
        ordering = ['name']

class MinusAuthor(models.Model):
    """
    represents Original artists, that perform minused records
    Auto populated by adding records
    """
    name = models.CharField(u"Ім’я автора мінусовок", max_length = 255)
    filetypes = models.ManyToManyField(FileType, 
            verbose_name = u"Типи файлів",
            help_text = u'Типи файлів, присутні у даного автора',
            null = True, blank = True, related_name = 'authors_have')

    def has_alternative(self):
        return self.records_by.filter(alternative = True).exists()

    def has_regular(self):
        return self.records_by.filter(alternative = False).exists()
        
    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return ('minus_by_author', [self.name])
    get_absolute_url = permalink(get_absolute_url)  # :D

    def delete(self):
        for r in self.records_by.all():
            author,created = MinusAuthor.\
                objects.get_or_create(name = u"Невідомий виконавець")
            r.author = author
            r.save()
        super(MinusAuthor, self).delete()

    class Meta:
        verbose_name = 'Автор записів'
        verbose_name_plural = 'Виконавці'
        ordering = ['name']


TEMPO_CHOICES = (
    ("slow",u"Повільна"),
    ("normal",u"Помірна"),
    ("fast",u"Швидка"),
)

GENDER_CHOICES = (
    ("all",u"Будь яка"),
    ("men",u"Чоловіча"),
    ("wemen",u"Жіноча"),
)

STAFF_CHOICES = (
    ("solo",u"Соло"),
    ("duo",u"Дует"),
    ("band",u"Ансамбль"),
    ("chour",u"Хор"),
    ("orchestra",u"Оркестр"),
    )

class MinusRecord(models.Model):
    """
    Model 
    That represents voiced-off record
    http://bitbucket.org/foomor/minus/wiki/MinusArhcive
    """
    user = models.ForeignKey('auth.User',
            related_name='uploaded_records')
    file = models.FileField(u'Файл',storage = audio_storage,
            blank=True, 
            null=True, upload_to = up_filename, max_length=2048)
    title = models.CharField('Назва',blank = True,
            help_text = "Назва композиції", max_length = 255)
    is_folk = models.BooleanField('Народна композиція',
            blank = True, default = False)
    alternative = models.BooleanField('Альтернативний запис',
            help_text = 'запис не є українською мінусовкою,\
            (інструменталки, пісні народів світу, тощо)',
            blank = True,
            default = False,
            )
    author = models.ForeignKey(MinusAuthor, verbose_name = u"Виконавець",
            related_name='records_by',blank = True, null = True) #foreignkey
    arrangeuathor = models.CharField('Автор аранжування', blank = True, 
            null = True, max_length = 50)
    annotation = models.TextField('Анотація',
            help_text = u'Додаткові дані, авторські права',
            blank = True)
    categories = models.ManyToManyField(MinusCategory, 
            verbose_name = u"Категорії",
            help_text = u'Жанри до яких належить даний запис. ',
            null = True, blank = True, related_name = 'records_in_category')
    thematics = models.CharField('Тематика', max_length = 30, blank = True, 
            null = True,
            help_text = u"Тематика даної композиції, наприклад:\
            повстанська, стрілецька, поховальна")
    tempo = models.CharField('Темп композиції', max_length = 10,
            choices=TEMPO_CHOICES, default = "normal" )
    staff = models.CharField('Виконавчий склад', max_length = 10,
            choices = STAFF_CHOICES, help_text = u"колектив, для якого\
            призначена дана мінусовка", default = "solo")
    gender = models.CharField('Стать виконавця', max_length = 10,
            choices = GENDER_CHOICES, default = "all")
    is_childish = models.BooleanField('Дитяча', default = False)
    is_amateur = models.BooleanField('Аматорська', default = False, 
            help_text = u"Дана композиція є аматорським записом")
    is_ritual = models.BooleanField('Обрядова', default = False,
            help_text = u"Виконується на весіллях, святах і т.п.")
    lyrics = models.TextField('Текст пісні', blank = True)
    plusrecord = models.URLField('Посилання на плюсовку',blank = True,
            null = True, help_text = "Посилання на файло-обмінник\
            або інше місце, звідки можна скачати оригінал",
            max_length=2048)
    pub_date = models.DateTimeField(auto_now_add = True)
    length = models.TimeField(default = datetime.time(0, 0, 0),\
                                                editable = False)
    bitrate = models.IntegerField(default = 0, editable = False )
    filesize = models.IntegerField(default = 0, editable = False )

    embed_video = models.TextField("Відео виконання",
            help_text = u'За бажанням можете вставити відео з\
            оригінальним виконанням композиції. Підтримувані\
            сервіси: youtube',
            blank = True, null = True)

    type = models.ForeignKey(FileType,
        related_name = 'matched_records')
    rating = RatingField('Рейтинг', range=5)



    def get_absolute_url(self):
        return ('minus_detail', [self.author, self.id])
    get_absolute_url = permalink(get_absolute_url)  # :D

    class Meta:
        verbose_name = u'Мінусовка'
        verbose_name_plural = u'Мінусовки на сайті'
        ordering = ['-pub_date']

    def __unicode__(self):
        try:
            return u"%s - %s" % (self.author, self.title)
        except MinusAuthor.DoesNotExist: #STRANGEBUUG!!!
            self.author, created = MinusAuthor.objects.get_or_create(name = "Невідомий Виконавець")
            self.save()
            return u"%s - %s" % (self.author, self.title)
            
class MinusPlusRecord(models.Model):
    """Plus-records that are uploaded to the site and attached to minuses"""
    minus = models.OneToOneField(MinusRecord,
        related_name = 'up_plusrecord', blank = True, null = True) 
    user = models.ForeignKey('auth.User')
    file = models.FileField('Файл',storage = audio_storage,
            help_text = 'Бітрейт файлу буде знижено', 
             upload_to = up_filename, max_length=2048)
    
    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return u"Плюсовка до %s " % self.minus.__unicode__()

class MinusStats(models.Model):
    """
    Dayly download-stat for minuses
    to range them in time.
    """
    date = models.DateField(auto_now_add = True)
    rate = models.IntegerField(default = 0)
    minus = models.ForeignKey(MinusRecord,
        related_name = 'downloads') 

class MinusWeekStats(models.Model):
    """
    Weekly download statistic
    Generated by every-day command
    """
    rate = models.IntegerField(default = 0)
    minus = models.ForeignKey(MinusRecord,
        related_name = 'weekly_downloads')

    class Meta:
        ordering = ('-rate',)


class CommentNotify(models.Model):
    """
    Integrative glue-model for notifying users about comments
    """
    comment = models.OneToOneField(Comment)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey('auth.User')
    is_seen = models.BooleanField(default = False)

class MinusStopWord(models.Model):
    """
    Stop words, used to remove on validation
    """
    word = models.CharField("Слово", max_length = 30,
        help_text = 'маленькими літерами')
    blocked = models.BooleanField("Блокувати",
        help_text = u'Типово слова автоматично виключаються з назв, якщо встановити цей пункт, то користувач буде повинен ввести іншу назву', default = False)

    def __unicode__(self):
        return u"Стоп-слово %s" % self.word

    class Meta:
        verbose_name = u'Стоп слово'
        verbose_name_plural = u'Стоп слова'

import signals
