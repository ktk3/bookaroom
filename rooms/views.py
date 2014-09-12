from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from rooms.models import *

def signin(request):
    return render(request, 'login.html')

def index(request):
    if request.user.is_authenticated():
        rooms_list = Room.objects.all().order_by('name')
        context = {'rooms_list': rooms_list}
        return render(request, 'rooms/index.html', context)
    else:
        return redirect('/')

def detail(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    return render(request, 'rooms/detail.html', {'room': room})

# def detail(request, poll_id):
#     poll = get_object_or_404(Poll, pk=room_id)
#     return render(request, 'room/detail.html', {'room': room})

def results(request, room_id):
    return HttpResponse("You're looking at the results of room %s." % room_id)

def detail2(request, room_name):
    return HttpResponse("You're looking at room %s." % room_name)

def book(request, room_id):
    return HttpResponse("You're voting on poll %s." % poll_id)





from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def book_a_room(request, room_id):
    p = get_object_or_404(Room, pk=room_id)
    try:
    	print p;
            #      selected_slot = p.free_slots.all".get(pk=request.POST['slot'])
    except (KeyError, FreeSlot.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'rooms/detail.html', {
            'room': p,
            'error_message': "You didn't select a time slot.",
        })
    else:
        # selected_slot.votes += 1
        # selected_slot.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('results', args=(p.id,)))