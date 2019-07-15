from django.core.management.base import BaseCommand, CommandError
from radio.streamer import RadioStreamer


class Command(BaseCommand):
    args = '<action>'
    help = 'Radiostation management'

    def handle(self, *args, **kwargs):
        streamer = RadioStreamer()
        for arg in args:
            if arg == 'run':
                streamer.stream_media()
            if arg == 'next':
                import ipdb
                ipdb.set_trace()

