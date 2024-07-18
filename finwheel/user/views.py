from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from requests import HTTPError
from user.models import *
from django.urls import reverse
from ai.models import *
import datetime
# Create your views here.

def index(request):
    return render(request, "home/index.html")

def login_view(request):
    if request.method == "GET":
        return render(request, "user/login.html")
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return HttpResponseRedirect(reverse("ai:dashboard"))
        else:
            # Return an 'invalid login' error message.
            return render(request, "user/login.html", {"Error": "Login Invalid"})


def register_view(request):
    if request.method == 'POST':
        email = request.POST["email"]
        username = request.POST["username"]
        fname = request.POST["first_name"]
        lname = request.POST["last_name"]
        password = request.POST["password1"]
        c_password = request.POST["password2"]
        if c_password == password and User.objects.filter(username=username).count() == 0:
            us = User(username=username, email=email, password=password)
            us.first_name = fname
            us.last_name = lname
            us.save()
            login(request, us)  # Log in the new user
            new_chat = Chat(for_user = us, date_created=datetime.datetime.now())
            new_chat.save()
            return HttpResponseRedirect(reverse('ai:dashboard'))  # Redirect to homepage after successful registration
        else:
            return render(request, 'user/register.html', {"Error": "Registration Failed"})
    else:
        return render(request, 'user/register.html')



@login_required(login_url='/user/login')
def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect(reverse("home:dashboard"))