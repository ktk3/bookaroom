from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages

def index(request):
    return render(request, 'base.html')

def rooms(request):
    return render(request, 'base.html')

def signout(request):
    logout(request)
    return redirect('/')

def signin(request):
    print "I'm here!"
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

