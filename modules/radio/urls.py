from django.conf.urls.defaults import *



urlpatterns = patterns('radio.views',
    url(r'^$', 'radio_page', name='radio_page'),
    url(r'^status/$', 'radio_status', name='radio_status'),
    )
