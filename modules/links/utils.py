# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site

def send_notification(instance, template='links/site_owner_notice.html',
                      recipient=[settings.FRIENDLINK_MODERATOR_EMAIL,]):
    default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
    current_domain = Site.objects.get_current().domain
    subject = 'Нове повідомлення від minus.lviv.ua'
    sender = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(template, {
        'site_url': '%s://%s' % (default_protocol, current_domain),
        'friendlink': instance,
    })

    send_mail(subject, message, sender, recipient, fail_silently=True)
