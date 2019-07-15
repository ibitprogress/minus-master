# -*- coding: utf-8 -*-

from django.contrib import admin
from users.models import UserProfile, UserActivity, StaffTicket
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from photos.admin import AlbumInline

def username_list_display(obj):
    return ("%s" % obj.user.username)
username_list_display.short_description = 'Ім’я користувача'

def email_list_display(obj):
    return ("%s" % obj.user.email)
email_list_display.short_description = 'Пошта'

def fullname_list_display(obj):
    return ("%s %s" % (obj.name, obj.surname))
fullname_list_display.short_description = 'Ім’я та прізвище'


class UserProfileInline(admin.StackedInline):
    #list_display = (username_list_display, email_list_display,
                    #fullname_list_display,)
    #list_filter = ('is_moderator',)
    #search_fields = ['user__username', 'user__email']
    model = UserProfile

class UserAdminInlined(UserAdmin):
    inlines = [UserProfileInline, AlbumInline]
    list_filter = ('is_staff', 'is_superuser', 'is_active')


class StaffTicketAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','pub_date', 'is_done')
    list_filter = ('is_done', 'pub_date')
    list_editable = ('is_done',)
    readonly_fields = ('user', 'content_type', 'object_id','url', 'message')
    change_form_template = 'users/admin_staff_ticket.html'
admin.site.register(StaffTicket, StaffTicketAdmin)
admin.site.register(UserActivity)
admin.site.unregister(User)
admin.site.register(User, UserAdminInlined)
