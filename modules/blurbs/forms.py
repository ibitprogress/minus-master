# -*- coding: utf-8 -*-
from django.conf import settings
from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from models import Blurb, GeoRegion, GeoCity, BlurbCategory, BUYSELL_CHOICES
from ck.fields import CKEditor
from blurbs.utils import classmaker


class DynamicCityForm(forms.Form):
    def __init__(self, *args, **kwargs):
        """
        dynamicaly regenerate choices
        sadly, hits database each time. But should be cached in view.

        """
        super(DynamicCityForm, self).__init__(*args, **kwargs)
        if self.data.has_key('georegion') and self.data['georegion']:
            self.fields['geocity'].queryset = GeoCity.objects.filter(\
                region__id = int(self.data['georegion']))
        elif self.initial.has_key('georegion') and self.initial['georegion']:
            self.fields['geocity'].queryset = GeoCity.objects.filter(\
            region__id = int(self.initial['georegion']))

        else:
            self.fields['geocity'].choices = (('','-----'),)
            self.fields['geocity'].widget.attrs = {'disabled':'true'}

class BlurbForm(forms.ModelForm, DynamicCityForm):
    __metaclass__ = classmaker()
    user = forms.ModelChoiceField(queryset=User.objects,
        widget=forms.HiddenInput)

    def clean(self):
        cd = self.cleaned_data
            
        if cd['title']:
            matches = Blurb.objects.filter(title = cd['title'])
            if matches:
                for m in matches:
                    if m.description == cd['description']:
                        e = forms.ValidationError(mark_safe(u"Такий запис вже існує"))
                        self._errors['title'] = e.messages
                        del cd['title']

        if not cd['category']:
            e = forms.ValidationError(mark_safe(u"Вкажіть будьласка категорію"))
            self._errors['category'] = e.messages
            del cd['category']
        return cd

    class Meta:
        model = Blurb
        widgets = {
                    'description': CKEditor(ck_attrs={'customConfig'\
                    : settings.MEDIA_URL+'js/ckeditor/minusconf.js'})
                }
        exclude = ('pub_date','city')

def generate_choices(model):
    """
    generate choices-dict for ChoiceField
    Not using django's ModelChoiceField because of it's limitations
    """
    return tuple([('all','Всі')]+[(obj.slug, obj.title) for obj in model.objects.all()])



class BlurbFilterForm(DynamicCityForm):
    def __init__(self, *args, **kwargs):
        super(BlurbFilterForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = generate_choices(BlurbCategory)

    category = forms.ChoiceField(label = "Категорія",
        choices=generate_choices(BlurbCategory),
        widget=forms.Select)
    buysell = forms.ChoiceField(label = "Куплю/продам",
        choices = tuple([('A','Все')]+list(BUYSELL_CHOICES)))
    georegion = forms.ModelChoiceField(label = "Регіон",
        queryset = GeoRegion.objects.all(), required = False)
    geocity = forms.ModelChoiceField(label = "Місто",
        queryset = GeoCity.objects.all(), required = False)
    unseen = forms.BooleanField(label = "З моменту останнього відвідування", 
        required = False)

