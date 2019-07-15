from django.conf import settings
from django.core.management.base import NoArgsCommand
from forum.models import Thread

from pytils.translit import slugify
 

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        empty_threads = Thread.objects.filter(posts=0)
        empty_threads.delete()
