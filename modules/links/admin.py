# -*- coding: utf-8 -*-

from django.contrib import admin
from links.models import FriendLink, FriendLinkCategory

class FriendLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'site', 'description', 'is_approved',)
    list_filter = ('is_approved',)
    search_fields = ['title', 'site']
    exclude = ('is_notified', 'date_created',)

admin.site.register(FriendLink, FriendLinkAdmin)
admin.site.register(FriendLinkCategory)
