from django.db.models import Sum
from django import template
from django.conf import settings
from vocal_contest.models import VocalContest



register = template.Library()
 
def callMethod(obj, methodName):
    method = getattr(obj, methodName)

    if obj.__dict__.has_key("__callArg"):
        ret = method(*obj.__callArg)
        del obj.__callArg
        return ret
    return method()

def args(obj, arg):
    if not obj.__dict__.has_key("__callArg"):
        obj.__callArg = []
    
    obj.__callArg += [arg]
    return obj

register.filter("call", callMethod)
register.filter("args", args)



@register.simple_tag
def guests_remaining():
    contest = VocalContest.objects.get_current()
    if contest and contest.is_real:
        count = (contest.realvocalcontestguest_set.\
        aggregate(Sum('places'))['places__sum'] or 0)\
        +(contest.realvocalcontestparticipant_set.\
        aggregate(Sum('places'))['places__sum'] or 0)\
        -contest.realvocalcontestguest_set.count()
    else:
        count = 0
    return str(count)
@register.inclusion_tag('vocal_contest/contest_status.html')
def contest_status():
    """
    shows contest status on the page
    """

    contest = VocalContest.objects.get_current()
    if contest:
        cont_dict =  {
        'contest': contest,
        'status': contest.status(),
        'MEDIA_URL':settings.MEDIA_URL,
        }
        if contest.is_real:
            cont_dict['participants_count'] = contest.\
                realvocalcontestparticipant_set.count()
            guest_count = (contest.\
                realvocalcontestguest_set.aggregate(Sum('places'))['places__sum'] or 0)
            participant_guest_count = (contest.\
               realvocalcontestparticipant_set.aggregate(Sum('places'))['places__sum'] or 0)

            cont_dict['guests_count'] = guest_count+participant_guest_count
        else:
            cont_dict['participants_count']= contest.participants.count()

    else:
        cont_dict =  {
        'contest': None,
        'status': 'future',
        }
    return cont_dict
