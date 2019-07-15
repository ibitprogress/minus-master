from django.core.management.base import NoArgsCommand
from minusstore.models import MinusRecord, MinusAuthor

class Command(NoArgsCommand):
    """
    remove authors with same names
    """

    def handle_noargs(self, **options):
        for author in MinusAuthor.objects.all():
            q = MinusAuthor.objects.filter(name = author.name)
            if q.count() > 1:
                print "duplicate authror %s %s" % (author.name, q.count())
                for a in q[1:]:
                    a.records_by.all().update(author = author)
                    a.delete()
