# -*- coding: utf-8 -*-

from django.conf import settings
from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from users.models import UserProfile, StaffTicket
from users.extras.widgets import LegacySelectDateWidget


class UserProfileEditForm(forms.ModelForm):
    """
    Represents a form for editing UserProfile objects.
    """  

    def __init__(self,*args,**kwargs):
        forms.ModelForm.__init__(self,*args,**kwargs)
        #iserting fields to make them apear first in the form
        #not last, like it is when adding fields in ordinary way
        self.fields.insert(0,'name',
            forms.CharField(label=u'Ім’я', max_length = 30, required = False)
        )
        self.fields.insert(1,'surname',
            forms.CharField(label=u'Прізвище', max_length = 30,required = False)
        )
    birthdate = forms.DateField(label=u'Дата народження',
                                widget=LegacySelectDateWidget,
                                required=False)

    class Meta:
        model = UserProfile
        exclude = ('user',  'status_title', 'status_css', 'banned', 'banned_until')

    def clean(self):
        cd = self.cleaned_data

        try:
            if cd['avatar'].size > settings.AVATAR_MAX_SIZE:
                e = forms.ValidationError(mark_safe(\
                u'Розмір файлу не повинен перевищувати: ' + \
                str(settings.AVATAR_MAX_SIZE/1024) + u'КБайт'))
                self._errors['avatar'] = e.messages
        except:
            pass

        return cd

    def save(self, force_insert=False, force_update=False, commit=True):
        p = super(UserProfileEditForm, self).save(commit=False)
        user = self.instance.user
        user.first_name = self.cleaned_data['name']
        user.last_name = self.cleaned_data['surname']
        user.save()
        if commit:
            p.save()
        self.save_m2m()
        return p

class BlockUserForm(forms.Form):
    banned_until = forms.DateField(label="Заблокувати до",
        )
    message = forms.CharField(label="Причина блокування",
        widget = forms.Textarea)  

class StaffTicketForm(forms.ModelForm):

    class Meta:
        model = StaffTicket
