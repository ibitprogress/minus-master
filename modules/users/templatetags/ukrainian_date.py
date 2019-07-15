# -*- coding:utf-8 -*-

import datetime
from django import template

register = template.Library()

@register.filter
def birthdate(value):
    """
    Takes no argument, only represents given
    date in ukrainian, example: '15 Червня 1995'
    """
    monthes = {
        1: u'Січня',
        2: u'Лютого',
        3: u'Березня',
        4: u'Квітня',
        5: u'Травня',
        6: u'Червня',
        7: u'Липня',
        8: u'Серпня',
        9: u'Вересня',
        10: u'Жовтня',
        11: u'Листопада',
        12: u'Грудня',
    }
    month = monthes[value.month]
    return u'%s %s %s' % (value.day, month, value.strftime('%Y'))

@register.filter
def postdate(value):
    """
    Represents post date as 25 Грудня 2010, о 17:50 or
    Сьогодні, o 15:20 if posted today. 
    """
    if value.date() == datetime.datetime.today().date():
        return u'Сьогодні, о %s:%s'  % (value.strftime('%H'), value.strftime('%M'))
    return u'%s, о %s:%s' % (birthdate(value), value.strftime('%H'), value.strftime('%M'))
