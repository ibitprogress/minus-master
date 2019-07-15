#!/usr/bin/env python

# usage: ./example.py /path/to/file1 /path/to/file2 ...
import pylibshout
import sys
import string
import time

from django.utils.encoding import smart_str

from minusstore.models import MinusRecord, FileType
from radio.models import RadioSong, RadioJingle, RadioPlaylist
#s.public = 0
# s.protocol = 'http' | 'xaudiocast' | 'icy'
# s.name = ''
# s.genre = ''
# s.url = ''
# s.public = 0 | 1
# s.audio_info = { 'key': 'val', ... }
#  (keys are shout.SHOUT_AI_BITRATE, shout.SHOUT_AI_SAMPLERATE,
#   shout.SHOUT_AI_CHANNELS, shout.SHOUT_AI_QUALITY)

class RadioStreamer(object):
    def __init__(self):
        self.stream = pylibshout.Shout()
        self.stream.host = 'localhost'
        self.stream.port = 8001
        self.stream.password = 'minussource'
        self.stream.mount = "/minusradio"
        self.stream.format = pylibshout.SHOUT_FORMAT_MP3
        self.stream.name = 'Minusradio'
        self.stream.open()
        
    def stream_media(self):
        """main streaming loop"""
        while True:
            self.stream_random_minus()
            self.stream_random_jingle()

    def stream_random_minus(self):
        ft = FileType.objects.get(type_name = 'audio')
        minusrec = ft.matched_records.order_by('?')[0]
        self.stream_minus(minusrec)

    def stream_minus(self,minusrec):
        print minusrec.title
        self.stream.metadata =  {'song':\
                smart_str('%s - %s' %(minusrec.title, minusrec.author.name))}
        self.stream_file(minusrec.file)

    def stream_random_jingle(self):
        print "jingle"
        self.stream_file(RadioJingle.objects.filter(enabled = True).order_by('?')[0].file)
        

    def stream_file(self, file):
        buf = file.read(8192)
        while buf:
            self.stream.send(buf)
            self.stream.sync()
            buf = file.read(8192)
        file.close()


