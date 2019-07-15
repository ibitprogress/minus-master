from django.conf import settings
from django.core.management.base import NoArgsCommand

from minusstore.models import MinusRecord


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        minuses = MinusRecord.objects.all()
        for minus in minuses:
            file_url = minus.file.url[:]
            minus.file.url = file_url.replace(settings.MEDIA_ROOT + '/', '')
            minus.save()
