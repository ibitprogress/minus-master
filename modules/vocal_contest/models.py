# -*- coding: utf-8 -*-
import datetime
import os.path
import pytils

from django.conf import settings
from django.db import models
from django.db.models import Count
from django.contrib.flatpages.models import FlatPage
from django.core.files.storage import FileSystemStorage


audio_storage = FileSystemStorage(location=settings.STORAGE_ROOT)


def up_filename(instance, filename):
    """
    generate filename to upload
    it consists of user-id/sha-hash/original-filename
    """
    basename,extension = os.path.splitext(filename)
    return u'files/contest/%d/%d/%s%s' % (instance.contest.pk,
            instance.user.pk,
            pytils.translit.slugify(basename),
            extension)

def reg_end():
    """function for date generation in default fields"""
    return datetime.date.today()+datetime.timedelta(\
        days = settings.CONTEST_REGISTRATION_END_DAYS)

def contest_end():
    """function for date generation in default fields"""
    return datetime.date.today()+datetime.timedelta(\
        days = settings.CONTEST_END_DAYS)


class VocalContestManager(models.Manager):
    def get_current(self):
        """
        return current contest it should be already started
        and the last one to finish
        """
        qs = super(VocalContestManager, self).get_query_set().\
            filter(start_date__lte = datetime.date.today()).\
            order_by('-end_date')
        if qs: return qs[0]
        else: return None
        

class VocalContest(models.Model):
    """Contest for vocalists"""

    title = models.CharField(u"Заголовок конкурсу", max_length = 60)
    description = models.TextField(u"Опис", max_length = 500, blank = True)
    rules = models.ForeignKey(FlatPage, verbose_name="Сторінка правил",
            blank = True, null = True)
    start_date = models.DateField(u"Початок конкурсу",
            default = datetime.date.today)

    registration_end_date = models.DateField(u"Завершення реєстрації",
            default = reg_end)
    end_date = models.DateField(u"Закінчення конкурсу",
            default = contest_end)

    is_real = models.BooleanField(u"Відбувається у реалі",
        default = False,
        blank = True,
        help_text = u"Якщо встановлено, система по іншому оброблятиме реєстрацію"
        )

    objects = VocalContestManager()

    def __unicode__(self):
        return u"%s" %  self.title 

    @models.permalink
    def get_absolute_url(self):
        if self.categories.all():
            return ('vocal_contest_filter', [self.categories.all()[0].id, 'rate'])
        else:
            return ('vocal_contest_archive')

    def status(self):
        today = datetime.date.today()
        if self.start_date <= today and self.end_date >= today:
            if self.registration_end_date >= today:
                return "open"
            else:
                return "closed"
        else:
            if self.start_date > today:
                return "future"
            elif self.end_date < today:
                return "finished"


    class Meta:
        verbose_name = u"Конкурс вокалістів"
        verbose_name_plural = u"Конкурси вокалістів"

class VocalContestCategoryManager(models.Manager):
    def get_cats(self, contest=None):
        """
        return categories for current contest
        """
        if not contest: contest = VocalContest.objects.get_current()
        # if we have no contests at all: we should check again
        if contest and contest.is_real: 
            participants_field = 'real_participants'
        else:
            participants_field = 'participants'
        return super(VocalContestCategoryManager, self).get_query_set().\
            filter(contest = contest).\
            annotate(participants_count = Count(participants_field)).\
            order_by('pk')


class VocalContestCategory(models.Model):
    title = models.CharField(u"Назва категорії", max_length = 60)
    description = models.TextField(u"Опис", max_length = 500, blank = True)
    contest = models.ForeignKey(VocalContest,related_name = 'categories')
    objects = VocalContestCategoryManager()

    def __unicode__(self):
        return u"%s" % self.title

    class Meta:
        verbose_name = u"Категорія конкурсу"
        verbose_name_plural = u"Категорії конкурсу"

class VocalContestParticipant(models.Model):
    user = models.ForeignKey('auth.user')
    contest = models.ForeignKey(VocalContest,
        default = VocalContest.objects.get_current,
        related_name = 'participants'

    )
    title = models.CharField(u'Заголовок', max_length = 120, 
        help_text = 'Якщо порожній, буде підставлено з міток файлу',
        blank = True)
    category = models.ForeignKey(VocalContestCategory, 
        verbose_name = "Категорія",
        related_name = 'participants')
    file = models.FileField(u'Файл',storage = audio_storage,
            upload_to = up_filename, max_length=2048,
            help_text = 'mp3 будь ласка')
    description = models.TextField(u'Коментар ', 
        max_length = 160,
        help_text = "Коротко, декілька слів про запис",
        blank = True
        )
    pub_date = models.DateTimeField(auto_now_add = True)
    
    @models.permalink
    def get_absolute_url(self):
        return ('vocal_contest_participant_detail',[self.id])

    class Meta:
        verbose_name = u"Учасник"
        verbose_name_plural = u"Учасники"

    def __unicode__(self):
        return '%s (%s)' % (self.title, self.category.title)



class RealVocalContestPerson(models.Model):
    user = models.ForeignKey('auth.user')
    contest = models.ForeignKey(VocalContest,
        default = VocalContest.objects.get_current,
        verbose_name = "Конкурс"
    )
    places = models.IntegerField("Зарезервовано місць",
        help_text = u"Ви можете вказати, скільки місць зарезервувати за столиками, включно з вашим",
        default = 1
        )
    is_payed = models.BooleanField("Оплачено", default = False)
    pub_date = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'Гість %s' % self.user.get_profile().fullname()


class RealVocalContestGuest(RealVocalContestPerson):
    class Meta:
        verbose_name = u"Гість конкурсу в реалі"
        verbose_name_plural = u"Гості"


class RealVocalContestParticipant(RealVocalContestPerson):
    category = models.ForeignKey(VocalContestCategory, 
        verbose_name = "Категорія",
        related_name = 'real_participants')
    info = models.TextField("Контакти", 
        help_text = u"Контактні дані(телефон, поштова адреса, то-що), щоб адміністрація могла з вами зв’язатися.",
        blank = True,
        null = True)
    requirements = models.TextField("Вимоги",
        help_text = u"Побажання до проведення конкурсу та тех-райдер",
        blank = True,
        null = True)
    
    class Meta:
        verbose_name = u"Учасник конкурсу в реалі"
        verbose_name_plural = u"Учасники в реалі"

    def __unicode__(self):
        return u'учасник %s (%s)' % (self.user.get_profile().fullname(),
            self.category.title)

    @models.permalink
    def get_absolute_url(self):
        return ('vocal_contest_filter',[self.category.id, 'date'])
