import datetime

from django.core.management.base import NoArgsCommand
from minusstore.models import MinusRecord, MinusAuthor, MinusCategory, FileType, MinusStats, MinusWeekStats

class Command(NoArgsCommand):
    """
    Find most downloaded reccords
    for last week

    It's quite expensive, so should not be used very often
    """

    def handle_noargs(self, **options):
        weekago = datetime.date.today()\
            - datetime.timedelta(weeks = 1)
        stats = MinusStats.objects.filter(date__gte = weekago)

        MinusWeekStats.objects.filter(rate__gt = 0).update(rate = 0)

        for stat in stats:
            weekstat,c = MinusWeekStats.objects.get_or_create(minus = stat.minus)
            weekstat.rate += stat.rate
            weekstat.save()
        MinusStats.objects.filter(date__lte = weekago).delete()

