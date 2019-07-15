from django.conf.urls.defaults import *
from haystack.views import SearchView

from djangoratings.views import AddRatingFromModel

from minusstore.models import MinusRecord
from minusstore.forms import MinusSearchForm

urlpatterns = patterns('minusstore.views',
    url(r'^$', 'minus_author_by_letter', name='minus_index'),
    url(r'^artist/$', 'minus_author_by_letter', name='minus_author_index'),
    url(r'^artist_alphabet/(?P<letter>(0-9|\w{1}))/$', 'minus_author_by_letter',
        name='minus_author_by_letter'),
    url(r'^artist/(?P<author>.*)/rec/(?P<id>\d+)/$', 'minus_detail', 
        name='minus_detail'),
    url(r'^artist/(?P<author>.*)/rec/download/(?P<id>\d+)/$', 'minus_download',
        name='minus_download'),
    url(r'^artist/(?P<author>.*)/ajax/type=(?P<type>\w*)&let=(?P<letter>(0-9|\w{0,1}))&class=(?P<t_class>\w*)/$',
        'minus_by_author',{'ajax':True}, name='minus_by_author_ajax'),
    url(r'^artist/(?P<author>.*)/$', 'minus_by_author', name='minus_by_author'),
    url(r'^type/(?P<type>\w+)/$', 'minus_by_type', name='minus_by_type'), 
    url(r'^date/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        'minus_time_archive', name = 'minus_archive_day'),
    url(r'^date/(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'minus_time_archive',
        name = 'minus_archive_month'),
    url(r'^date/(?P<year>\d{4})/$', 'minus_time_archive',
        name = 'minus_archive_year'),
    url(r'^upload/f/$', 'minus_flash_upload', name='minus_flash_upload'),
    url(r'^upload/plus/done/$', 'plus_upload_done', name='minus_plus_upload_done'),
    url(r'^upload/plus/$', 'plus_upload', name='minus_plus_upload'),
    url(r'^upload/plus/user/(?P<user>\d+)/$', 'plus_upload', name='minus_plus_upload_user'),
    url(r'^upload/$', 'minus_upload', name='minus_upload'),
    url(r'^mass_upload/$', 'minus_mass_upload', name='minus_mass_upload'),
    url(r'^edit/(?P<user>[-\.\w\d]+)/(?P<id>\d+)/$', 'minus_edit',
        name='minus_edit'),
    url(r'^plus_delete/(?P<id>\d+)/$', 'plus_delete',
        name='plus_delete'),
    url(r'^delete/(?P<user>[-\.\w\d]+)/(?P<id>\d+)/$', 'minus_delete',
        name='minus_delete'),
    url(r'^user/(?P<username>[-\.\w\d]+)/$', 'minus_by_user',
        name='minus_by_user'),
    url(r'search/$', SearchView(form_class=MinusSearchForm,
        template='search/minus_search.html'), name='minus_search'),
    url(r'comments/(?P<username>[-\.\w\d]+)/$', 'comments_for',
        name='comments_for'),

    url(r'^minus_to_audiorec/(?P<id>\d+)/$', 'minus_to_audiorec',
        name='minus_to_audiorec'),
    url(r'^audiorec_to_minus/(?P<id>\d+)/$', 'audiorec_to_minus',
        name='audiorec_to_minus'),
    
    )

urlpatterns += patterns('',
    url(r'rate/(?P<object_id>\d+)/(?P<score>\d+)/', AddRatingFromModel(), {
        'app_label': 'minusstore',
        'model': 'minusrecord',
        'field_name': 'rating',
    }, name='rate_on_minus'),
)
