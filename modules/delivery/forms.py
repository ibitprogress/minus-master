# -*- coding: utf-8 -*-

from django import forms

from delivery.models import Subscriber


class SubscriberForm(forms.ModelForm):

    class Meta:
        model = Subscriber

class SubscriberAddForm(forms.ModelForm):

    class Meta:
        model = Subscriber
        exclude = ('is_subscribed')
