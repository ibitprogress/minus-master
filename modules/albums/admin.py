# -*- coding: utf-8 -*-
 
from django.contrib import admin
from models import Audio, AudioAlbum

class AudioAdminInline(admin.StackedInline):
    model = Audio
    extra = 0
    exclude = ('user',)

class AudioAlbumAdmin(admin.ModelAdmin):
    inlines = [AudioAdminInline]
    exclude = ('user',)
        
admin.site.register(AudioAlbum, AudioAlbumAdmin)
