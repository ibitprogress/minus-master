# -*- coding: utf-8 -*-
import threading
import time
from datetime import datetime

from django.core.mail import send_mass_mail, EmailMessage, get_connection

from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.core.validators import email_re

from django.contrib import messages


from users.models import UserProfile
def is_valid_email(email):
    return True if email_re.match(email) else False

class AsyncMassmail(threading.Thread):
    """fork sending emails into background process"""
    def __init__(self, instance):
        self.instance = instance
        threading.Thread.__init__(self)

    def run(self):
        default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
        current_domain = Site.objects.get_current().domain
        subject = self.instance.subject
        message = render_to_string('delivery/massmail.html', {
            'site_url': '%s://%s' % (default_protocol, current_domain),
            'mail': self.instance,
        })

        connection = get_connection(username=None, password=None,
                                fail_silently=True)
        msgs = []
        for profile in UserProfile.objects.filter(is_admin_subscribed=True):
            try:
                if profile.user.email and is_valid_email(profile.user.email) :
                    #time.sleep(0.1) #do not overload our server
                    msg = EmailMessage(subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [profile.user.email])
                    msg.content_subtype = 'html'
                    msgs.append(msg)
            except User.DoesNotExist:
                profile.delete()

        connection.send_messages(msgs)
        for user in User.objects.filter(is_superuser = True):
            user.message_set.create(message = 'Розсилку надіслано')
        
        

def send_massmail(sender, instance, signal,*args, **kwargs):

    if instance.is_ready:
        mails = AsyncMassmail(instance)
        mails.start()


def send_happybirthday(mail=None):
    public_birthdates = UserProfile.objects.exclude(birthdate=None)
    today = datetime.today()
    birthday_users = public_birthdates.filter(birthdate__month=today.month,
                                              birthdate__day=today.day)

    default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')

    if not birthday_users:
        return

    try:
        current_domain = Site.objects.get_current().domain
        subject = mail.happybirthday_title
        for birthday_user in birthday_users:
            message = render_to_string('delivery/happybirthday.html', {
                'site_url': '%s://%s' % (default_protocol, current_domain),
                'body': mail.happybirthday_body,
                'banner': mail.happybirthday_banner,
                'user': birthday_user,
            })
            msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL,
                               [birthday_user.user.email,])
            msg.content_subtype = 'html'
            msg.send(fail_silently=True)

    except Exception, e:
        pass #fail silently


