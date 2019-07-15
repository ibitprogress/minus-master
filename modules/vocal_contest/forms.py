# -*- coding: utf-8 -*-
from django.conf import settings
from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from models import VocalContestParticipant, VocalContest, VocalContestCategory, RealVocalContestParticipant, RealVocalContestGuest

from minusstore.forms import BaseMusicForm


###abstract###

class DefaultVocalContestForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects,
        widget=forms.HiddenInput) 
    contest = forms.ModelChoiceField(queryset=VocalContest.objects,
        widget=forms.HiddenInput) 

class DefaultVocalContestParticipantForm(BaseMusicForm, DefaultVocalContestForm):
    def __init__(self, *args, **kwargs):
        super(DefaultVocalContestParticipantForm,self).\
            __init__(*args, **kwargs)
        #get fresh categories on each init
        self.fields['category'].queryset =\
            VocalContestCategory.objects.get_cats()
    category = forms.ModelChoiceField(queryset=\
        VocalContestCategory.objects,
        label = 'Категорія')
    
###real###
    
class RealVocalContestGuestForm(DefaultVocalContestForm):
    class Meta:
        model = RealVocalContestGuest
        exclude = ('is_payed',)

class RealVocalContestParticipantForm(DefaultVocalContestParticipantForm):
    class Meta:
        model = RealVocalContestParticipant
        exclude = ('is_payed',)

class VocalContestParticipantForm(DefaultVocalContestParticipantForm):
    def __init__(self, *args, **kwargs):
        super(VocalContestParticipantForm, self).__init__(*args, **kwargs)

        # change a widget attribute:
        self.fields['description'].widget.attrs["rows"] = 2
    
    class Meta:
        model = VocalContestParticipant
    
    def clean(self):
        cd = self.cleaned_data
        if cd.has_key('file') and cd['title'] == u'':
            try:
                self.get_mp3info(cd['file'].file.name)
                cd['title'] = self.mp3info['TIT2'].text[0]
            except (ValueError, KeyError, AttributeError):
                cd['title'] = cd['file'].name[:-4]  #cut .mp3

        dups = VocalContestParticipant.objects.filter(\
            category = cd['category'], user = cd['user'])
        if dups:
            e = forms.ValidationError(mark_safe(\
            u'Ви можете додати лише один запис до однієї категорії, ваш файл: <a href="%s">%s</a> '\
            %( dups[0].get_absolute_url(),dups[0].title )))
            self._errors['category'] = e.messages
            del cd['category']


        return cd
                

