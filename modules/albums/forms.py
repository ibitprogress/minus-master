# -*- coding: utf-8 -*-
from django import forms
from models import BaseAlbum, AudioAlbum, Audio
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from blurbs.utils import classmaker





class AudioAlbumForm(forms.ModelForm):

    user = forms.ModelChoiceField(queryset=User.objects,
        widget=forms.HiddenInput)

    class Meta:
        model = AudioAlbum
        exclude =  ('content_type','object_pk','slug','pub_date')
    

class AudioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """dynamically put choices regarding to user"""
        super(AudioForm, self).__init__(*args, **kwargs)
        if self.data.has_key('user')\
        and self.data['user']:
            self.fields['album'].queryset = AudioAlbum.objects.filter(\
                user__id = int(self.data['user']))
        elif self.initial.has_key('user')\
        and self.initial['user']:
            self.fields['album'].queryset = AudioAlbum.objects.filter(\
                user__id = int(self.initial['user']))
    user = forms.ModelChoiceField(queryset=User.objects,
        widget=forms.HiddenInput)

    class Meta:
        model = Audio
        exclude = ('pub_date')


    def clean(self):
        cd = self.cleaned_data

        if not cd.has_key('file'):
            e = forms.ValidationError(mark_safe(\
            u'Додайте будь ласка файл' ))
            self._errors['file'] = e.messages
        else:

            if cd['file'].name.split(".")[-1] != 'mp3':
                e = forms.ValidationError(mark_safe(\
                u'Завантажуйте будьласка лише mp3-файли' ))
                self._errors['file'] = e.messages

            if cd['file'].size > settings.MAX_FILE_SIZE:
                e = forms.ValidationError(mark_safe(\
                u'Розмір файлу не повинен перевищувати: ' + \
                str(settings.MAX_FILE_SIZE/1024/1024) + u'МБайт'))
                self._errors['file'] = e.messages

            

        return cd

