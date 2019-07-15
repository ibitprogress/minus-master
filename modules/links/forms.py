# -*- coding: utf-8 -*-

from django import forms

from captcha.fields import CaptchaField
from links.models import FriendLink


class FriendLinkAddForm(forms.ModelForm):
    """
    Represents form for adding friend link objects
    """
    captcha = CaptchaField(label='Каптча')

    class Meta:
        model = FriendLink
        exclude = ('is_approved', 'date_created', 'date_approved',
                   'is_notified')
