# -*- coding: utf-8 -*-
import datetime

from django.views.generic.list_detail import object_list, object_detail
from django.views.generic.create_update import create_object, update_object,delete_object
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse, Http404
from django.views.decorators.cache import cache_page
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from voting.models import Vote

from models import VocalContest, VocalContestCategory, VocalContestParticipant, RealVocalContestGuest, RealVocalContestParticipant
from forms import VocalContestParticipantForm, RealVocalContestGuestForm, RealVocalContestParticipantForm

@cache_page(60*2)
def vocal_contest_index(request):
    contest = VocalContest.objects.get_current()
    if not contest:
        raise Http404
    categories = VocalContestCategory.objects.get_cats(contest)
    if categories: cat_id = categories[0].id
    else: cat_id = 0    #categories should be filterable, not get
    if contest.status() == 'open':
        return vocal_contest_filter(request, cat_id, 'date')
    else:
        return vocal_contest_filter(request, cat_id, 'rate')


@cache_page(60)
def vocal_contest_filter(request, cat_id, order = 'date'):
    """
    FIXME
    heavy and not the most optimized view

    filter objects by categories and order
    them by dates or votes

    by votes: first we get all the votes for participant
    order them by value, get their obj-id's 
    and get objects themselves in same order
    """
    category = get_object_or_404(VocalContestCategory, id = cat_id)
    categories = VocalContestCategory.objects.get_cats(category.contest)
    if category.contest.is_real:
        qs_model = RealVocalContestParticipant
        guest_list = category.contest.realvocalcontestguest_set.all()
        
    else:
        qs_model = VocalContestParticipant
        guest_list = []
    qs = qs_model.objects.filter(category = category, contest = category.contest).order_by('pub_date')

    #category.contest - if category was used previously

    if order == 'rate' and not category.contest.is_real:
        # This code is based on get_top funciton in votes.managers and
        # adapted to our needs
        ctype = ContentType.objects.get_for_model(VocalContestParticipant)
        query = """
        SELECT object_id, SUM(vote) as %s
        FROM %s
        WHERE content_type_id = %s
        GROUP BY object_id""" % (
            connection.ops.quote_name('score'),
            connection.ops.quote_name(Vote._meta.db_table),
            ctype.id,
        )
        if settings.DATABASE_ENGINE == 'mysql':
            having_score = connection.ops.quote_name('score')
        else:
            having_score = 'SUM(vote)'

        having_sql = ' ORDER BY %(having_score)s DESC' % {'having_score': having_score}

        query += having_sql

        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        # we got votes and object-id's in descending order
        # now we need ojbects themselves in this ordering
        # filter(id__in) does not work, because it breaks order
        plusvotd = [] #positive voted
        minusvotd = [] #negative voted
        for id,score in results:
            try:
                if score > 0:
                    plusvotd.append(qs.get(id = id))
                else:
                    minusvotd.append(qs.get(id = id))
            except VocalContestParticipant.DoesNotExist:
                pass
        #append objects that have been not voted
        unvotd = list(qs.exclude(id__in = [id for id,score in results]))
        qs = plusvotd + unvotd + minusvotd

    
    return render_to_response('vocal_contest/filter.html',
        {'object_list':qs,
            'order':order,
            'categories':categories,
            'current_category':category,
            'guest_list':guest_list
        
        }, 
        context_instance=RequestContext(request))

@login_required
def vocal_contest_participate(request):
    """
    if there is open contest:
    if it has rules: show rules first
    then show participation form
    """
    contest = VocalContest.objects.get_current()
    if contest and contest.status() == 'open':
        if contest.rules and not request.method == 'POST':
            return render_to_response('flatpages/agree.html',
                {'flatpage':contest.rules},
                context_instance=RequestContext(request))
        else:
            if request.POST.has_key('__confirm__'): 
                # confirmation form is submited. 
                # so we delete it's data and show up participate form
                request.POST = {}
                request.method = 'GET'
            if contest.is_real:
                form_class = RealVocalContestParticipantForm
            else:
                form_class = VocalContestParticipantForm

            return create_object(
                request,
                form_class = form_class,
                login_required = True,
                template_name = 'vocal_contest/participate.html',
                extra_context = {'contest':contest,} 
                )
    else: return redirect(vocal_contest_index)

@login_required
def vocal_contest_participant_delete(request,id):
    vcp = get_object_or_404(VocalContestParticipant.objects, id = id)
    if vcp.user == request.user or request.user.is_staff:
        return delete_object(
            request,
            model = VocalContestParticipant,
            object_id = id,
            post_delete_redirect = reverse('vocal_contest_index'),
            login_required = True,
            template_name = 'shared/object_delete_confirm.html',
            )
    else: raise Http404

@cache_page(60)
def vocal_contest_participant_detail(request, id):
    return object_detail(
        request,
        queryset = VocalContestParticipant.objects.all(),
        object_id = id,
        template_name = 'vocal_contest/participant_detail.html',
        )
    

def vocal_contest_guest(request):
    contest = VocalContest.objects.get_current()
    if contest\
    and contest.status() == 'open'\
    and contest.is_real:
        rvc = RealVocalContestGuest.objects.filter(user = request.user)
        if rvc:
            return update_object(
                request,
                form_class = RealVocalContestGuestForm,
                object_id = rvc[0].id, #should be
                login_required = True,
                template_name = 'vocal_contest/guest.html',
                post_save_redirect = reverse('vocal_contest_index'),
                extra_context = {'contest':contest,'edit':True} 
                )

        else:
            return create_object(
                request,
                form_class = RealVocalContestGuestForm,
                login_required = True,
                template_name = 'vocal_contest/guest.html',
                post_save_redirect = reverse('vocal_contest_index'),
                extra_context = {'contest':contest,} 
                )
    else: return redirect(vocal_contest_index)
    

def vocal_contest_archive(request):
    return object_list(
        request,
        queryset = VocalContest.objects.filter(\
            end_date__lte = datetime.date.today()).\
            order_by('end_date'),
        template_name = 'vocal_contest/vocal_contest_archive.html',
        )
