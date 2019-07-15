# -*- coding: utf-8 -*-

from django.contrib import admin
from delivery.models import Subscriber, SubscribersMailSettings, MassMail


class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'frequency', 'is_subscribed')
    list_filter = ('frequency', 'is_subscribed')
    search_fields = ['email',]

class SubscribersMailSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Щодня', {
            'fields': ('daily_title', 'daily_body', 'daily_banner')
        }),
        ('Раз на тиждень', {
            'fields': ('weekly_title', 'weekly_body', 'weekly_banner')
        }),
        ('Раз на два тижні', {
            'fields': ('weekly_2_title', 'weekly_2_body', 'weekly_2_banner')
        }),
        ('Раз на місяць', {
            'fields': ('monthly_title', 'monthly_body', 'monthly_banner')
        }),
        ('Привітання з Днем Народження', {
            'fields': ('happybirthday_title', 'happybirthday_body', 'happybirthday_banner')
        }),
    )

admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(SubscribersMailSettings, SubscribersMailSettingsAdmin)
admin.site.register(MassMail)
