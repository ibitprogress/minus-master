from django.conf.urls.defaults import *
from voting.views import vote_on_object
from models import VocalContestParticipant



urlpatterns = patterns('vocal_contest.views',
    url(r'^$', 'vocal_contest_index', name='vocal_contest_index'),
    url(r'^show/(?P<cat_id>\d+)/(?P<order>[d|r]ate)/$', 'vocal_contest_filter', name='vocal_contest_filter'),
    url(r'^participate/$', 'vocal_contest_participate', name='vocal_contest_participate'),
    url(r'^guest/$', 'vocal_contest_guest', name='vocal_contest_guest'),
    url(r'^detail/(?P<id>\d+)/$', 'vocal_contest_participant_detail',
        name='vocal_contest_participant_detail'),
    url(r'^delete/(?P<id>\d+)/$', 'vocal_contest_participant_delete',
        name='vocal_contest_participant_delete'),
    url(r'^archive/$', 'vocal_contest_archive', name='vocal_contest_archive'),
    
    )

vc_dict = {
    'model': VocalContestParticipant,
    'template_name': 'vocal_contest/participatnt_detail.html',
    'allow_xmlhttprequest': True,
}

urlpatterns += patterns('',
    url(r'^vote/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$',
        vote_on_object, vc_dict, name='vote_on_user'),                       
)
