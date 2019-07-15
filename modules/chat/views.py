# Create your views here.
from models import ChatRoom
from jchat.models import Room
from forms import RoomCreateForm
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

@login_required
def chat_room(request, obj_id):
    roomholder = get_object_or_404(ChatRoom, id=obj_id)
    room = Room.objects.get_or_create(roomholder)
    return render_to_response('chat/room.html', {'holdr':roomholder, 'chat_id':room.id},
          context_instance=RequestContext(request))

@login_required
def create_room(request):

    initial = {'user':request.user.pk}
    if request.method == 'POST':
        form = RoomCreateForm(request.POST)
        if form.is_valid():
            room = form.save()
            return redirect(room)
    else:
        form = RoomCreateForm(initial=initial)

    return render_to_response('chat/create.html', {'form':form},
          context_instance=RequestContext(request))

@login_required
def delete_room(request, id):
    roomholder = get_object_or_404(ChatRoom, id=id)
    if request.user == roomholder.user or request.user.is_staff:
        roomholder.delete()
    return redirect(reverse('room_list'))

    
