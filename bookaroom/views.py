from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from rooms.models import *
from rooms.validators import *

def rooms(request):
    return render(request, 'index.html')

def book(request):
    room_id = request.POST['input_room']
    input_room = Room.objects.get(id=room_id)
    input_date = request.POST['input_date']
    input_begin = request.POST['input_begin']
    input_end = request.POST['input_end']
    availabile = TimeSlot.objects.all().filter(room=input_room, date=input_date)
    availabile = availabile.exclude(begin_time__gte = input_begin)
    availabile = availabile.exclude(end_time__lte = input_end)
    context = {'availabile': availabile}
    #TODO create new slots if user wants to book
    return render(request, 'book.html', context)

def book_form(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'book_form.html', context)

def find_slots(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'find_slots.html', context)

def find_rooms(request):
    return render(request, 'find_rooms.html')

def slots(request):
    if request.user.is_authenticated():
        slots_list = TimeSlot.objects.all().order_by('room')
        context = {'slots_list': slots_list}
        return render(request, 'slots.html', context)
    else:
        return redirect('/')

def slot_detail(request, slot_id):
    slot = get_object_or_404(TimeSlot, pk=slot_id)
    validate_dummy_slot(slot_id)
    return render(request, 'rooms/slot_detail.html', {'slot': slot})

def signout(request):
    logout(request)
    return redirect('/')

def signin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
        else:
            messages.error(request, 'Account locked')
    else:
        messages.error(request, 'Incorrect userame or password')
    return redirect('/')

