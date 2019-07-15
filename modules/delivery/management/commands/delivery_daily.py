from django.core.management.base import NoArgsCommand
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site

import sys

from delivery.models import Subscriber, SubscribersMailSettings
from delivery.utils import send_happybirthday
from minusstore.signals import timed_arivals

DEFAULT_PROTOCOL = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
CURRENT_DOMAIN = Site.objects.get_current().domain
MAIL = SubscribersMailSettings.objects.latest()
records = timed_arivals('day')

 
class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        send_happybirthday(mail=MAIL)

        subject = MAIL.daily_title
        subscribers = Subscriber.objects.get_daily()

        if not subscribers:
            sys.stderr.write('Ooops, you have no daily subscribers')
        for subscriber in subscribers:
            message = render_to_string('delivery/mail.html', {
                'body': MAIL.daily_body,
                'banner': MAIL.daily_banner,
                'site_url': '%s://%s' % (DEFAULT_PROTOCOL, CURRENT_DOMAIN),
                'subscriber_url': subscriber.get_absolute_url(),
                'records': records,
            })
            msg = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL,
                      [subscriber.email,])
            msg.content_subtype = 'html'
            msg.send(fail_silently=True)
