from django.core.management.base import NoArgsCommand
import datetime
 
from blurbs.models import Blurb
class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        bs = Blurb.objects.filter(pub_date__lte = datetime.date.today()-datetime.timedelta(days = 60))
        print "Deleting %s blurbs" % bs.count()
        bs.delete()
        print "done"

