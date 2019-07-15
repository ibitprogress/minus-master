import datetime

from django.core.management.base import NoArgsCommand
from hitcount.models import Hit
from django.conf import settings
class Command(NoArgsCommand):
    """
    remove old hits
    """

    def handle_noargs(self, **options):
        timetolive = datetime.date.today()\
            - datetime.timedelta(days = settings.HITCOUNT_KEEP_HIT_ACTIVE['days'])
        Hit.objects.filter(created__lte = timetolive).delete()

