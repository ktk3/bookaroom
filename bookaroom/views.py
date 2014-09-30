from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from rooms.models import *
from rooms.validators import *
from datetime import time, date

def rooms(request):
    return render(request, 'index.html')

def confirm_book(request):
    room_id = request.POST['input_room']
    input_room = Room.objects.get(id=room_id)
    input_date = request.POST['input_date']
    input_begin = request.POST['input_begin']
    input_end = request.POST['input_end']
    availabile = TimeSlot.objects.all().filter(room=input_room, date=input_date)
    availabile = availabile.exclude(begin_time__gt = input_begin)
    availabile = availabile.exclude(end_time__lt = input_end)
    slot = []
    if availabile.count() == 1:
        slot = availabile[0]
    context = {'slot': slot, 'begin': input_begin, 'end': input_end}
    return render(request, 'confirm_book.html', context)

def book(request):
    #TODO with atomic here!!!!
    slot_id = request.POST['slot_id']
    slot = TimeSlot.objects.get(id=slot_id)
    begin = request.POST['begin']
    end = request.POST['end']
    begin_parts = begin.split(':')
    begin_h = int(begin_parts[0])
    begin_m = int(begin_parts[1])
    end_parts = end.split(':')
    end_h = int(end_parts[0])
    end_m = int(end_parts[1])
    slot.book(time(begin_h, begin_m), time(end_h, end_m))
    context = {'slot': slot, 'begin': begin, 'end': end}
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
        slots_list = TimeSlot.objects.all().order_by('room', 'date', 'begin_time')
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
