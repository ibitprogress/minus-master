from django import template
from django.conf import settings
from django.contrib.auth.models import User

from datetime import datetime, timedelta

from users.models import UserActivity, UserProfile, UserRating, StaffTicket

register = template.Library()


@register.inclusion_tag('users/user_online.html')
def user_online(num):
    """
    Represents user logged within last 15 minutes
    """
    fifteen_minutes = datetime.now() - timedelta(minutes=15)
    sql_datetime = datetime.strftime(fifteen_minutes,
                                     '%Y-%m-%d %H:%M:%S')
    users = UserActivity.objects.filter(last_activity_date__gte=sql_datetime,
            user__is_active__exact=1).order_by('-last_activity_date')[:num]
    return {
        'active_users': users,
    }

@register.inclusion_tag('users/user_online.html')
def moderators():
    """
    Represents list of moderators
    """
    users = UserProfile.objects.filter(user__is_staff = True)
    return {
        'active_users': users,
        'moders': True,
    }

@register.inclusion_tag('users/birthday_today.html')
def birthday_today():
    """
    Represents list of users who have birthday today
    """
    public_birthdates = UserProfile.objects.exclude(birthdate=None,
                                                   hide_birthdate=True)
    today = datetime.today()
    birthday_users = public_birthdates.filter(birthdate__month=today.month,
                                             birthdate__day=today.day)
    return {
        'birthday_users': birthday_users,
    }


@register.inclusion_tag('users/top_rated.html')
def top_users():
    """
    Represents N top rated objects. N=TOP_RATED_LIMIT
    """
    users = UserRating.objects.all().order_by("-rating")[:settings.TOP_RATED_LIMIT]
    
    return {
        'top_users': users,
    }

@register.simple_tag
def open_staff_tickets():
    count = StaffTicket.objects.filter(is_done = False).count()
    if count: return '(%s)' % count
    else: return ''
