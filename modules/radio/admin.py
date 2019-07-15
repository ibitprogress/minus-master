# -*- coding: utf-8 -*-

from django.contrib import admin
from models import RadioPlaylist, RadioJingle, RadioSong

admin.site.register(RadioPlaylist)
admin.site.register(RadioJingle)
admin.site.register(RadioSong)
