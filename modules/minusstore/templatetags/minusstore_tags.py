# -*- coding: utf-8 -*-
from django.db.models import permalink
from django.conf import settings
from string import ascii_uppercase
from django import template
from django.conf import settings
import datetime
from django.core.urlresolvers import reverse

from minusstore.models import MinusRecord, FileType, MinusCategory, MinusWeekStats, MinusStats, CommentNotify
register = template.Library()

@register.simple_tag
def edit_object(obj):
    """
    Return a link for editing object in admin site
    """
    return reverse('admin:%s_%s_change' % (obj._meta.app_label,
                                           obj._meta.module_name),
                                           args=(obj.id,))


class LettersNode(template.Node):
    def __init__(self):
        alphabet = ascii_uppercase+u"АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
        numbers = "0-9"
        letters = []
        for letter in alphabet:
            letters.append(letter)
        letters.insert(0,numbers)
        self.letters = letters

    def render(self, context):
        context['letters'] = self.letters
        return ''

def letters(parser, token):
    return LettersNode()

letters = register.tag(letters)


class MonthMinusNode(template.Node):
    def __init__(self):
        self.today = datetime.date.today()
        self.minuses = MinusRecord.objects.all().filter(pub_date__year = self.today.year, pub_date__month = self.today.month)

    def render(self,context):
        context['month_minuses'] = self.minuses
        return ''

def monthminuses(parser, token):
    return MonthMinusNode()

letters = register.tag(monthminuses)

class StatisticsNode(template.Node):
    """
    populate context with two variables:
    total count of uploaded records
    statisitcs on records by type and category
    """
    def __init__(self):
        self.allreccords = MinusRecord.objects.count()
        by_type = []
        types = []
        for type in FileType.objects.all():
            by_cat = []
            types.append(type.display_name)
            min = MinusRecord.objects.filter(type = type)
            by_cat.append(type.display_name)
            by_cat.append(min.filter(is_childish = True).count())   #childish
            by_cat.append(min.filter(is_folk = True).count())       #folk
            by_cat.append(min.count() - by_cat[1])          #estrada = all - folk
            by_type.append(by_cat)
        cats  = ["","Дитячі", "Народні", "Естрадні"]
        by_type.insert(0, cats)
        self.stats = by_type
    
    def render(self, context):
        context['statistics'] = self.stats
        context['records_count'] = self.allreccords
        return''

def statistics(parser, token):
    return StatisticsNode()

statistics = register.tag(statistics)




class DateMinusHolder:
    """Container, to group minuses by date"""
    def __init__(self, date):
        self.date = date
        self.minuses = []

@register.inclusion_tag('minusstore/latest_arivals_block.html')
def latest_arivals_block(num):
    """
    Represents minuses uploaded for last few days
    count of minuses to display specified
    """
    minuses = MinusRecord.objects.all().order_by('-pub_date')[:num]
    #now we group them by date
    holdr = DateMinusHolder(datetime.datetime.now().date())
    new_minuses = [holdr]

    for minus in minuses:
        date = minus.pub_date.date()
        if holdr.date == date:
            holdr.minuses.append(minus)
        else:
            holdr = DateMinusHolder(date)
            holdr.minuses.append(minus)
            new_minuses.append(holdr)
    
    return {
        'new_minuses' : new_minuses,
    }

@register.inclusion_tag('minusstore/top_rated.html') #different template
def top_rated_week(model):
    """ Represents list of top rated object in the given model """
    if model == 'MinusRecord':
        top_rated_objects = MinusWeekStats.objects.filter(rate__gt=0)\
        .order_by('-rate')[:settings.TOP_RATED_LIMIT]
    return {
        'top_rated_objects': top_rated_objects,
    }


@register.inclusion_tag('minusstore/tag_comments_for.html')
def newcomments(user):
    comments = CommentNotify.objects.filter(user = user)
    if comments:
        num = comments.filter(is_seen = False).count()
        return {
            'comments':comments,
            'num':num,
            'user':user,
            'MEDIA_URL':settings.MEDIA_URL, #HACK :(
        }
    else:
        return None



