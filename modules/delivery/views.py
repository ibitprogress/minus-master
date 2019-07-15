from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext

from delivery.forms import SubscriberForm, SubscriberAddForm
from delivery.models import Subscriber

def delivery_detail(request, hash, id):
    subscriber = get_object_or_404(Subscriber, id=int(id), hash=hash)
    if request.method == 'POST':
        form = SubscriberForm(request.POST, instance=subscriber)
        if form.is_valid():
            subscribption = form.save(commit=False)
            subscribption.save()
            return redirect('/')
    else:
        form = SubscriberForm(instance=subscriber)

    return render_to_response('delivery/subscription.html',
                              {'subscriber': subscriber,
                               'form': form},
                             context_instance=RequestContext(request))

def delivery_add(request):
    if request.user.is_authenticated():
        initial = {'email': request.user.email}
    else:
        initial = {}
    if request.method == 'POST':
        form = SubscriberAddForm(request.POST, initial=initial)
        if form.is_valid():
            subscribption = form.save(commit=False)
            subscribption.save()
            return redirect('/')
    else:
        form = SubscriberAddForm(initial=initial)

    return render_to_response('delivery/add.html',
                              {'form': form},
                             context_instance=RequestContext(request))
