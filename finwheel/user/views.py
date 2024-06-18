from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from requests import HTTPError
from user.models import *
from django.urls import reverse
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
        fname = request.POST["username"]
        lname = request.POST["username"]
        password = request.POST["password"]
        c_password = request.POST["confirm_password"]
        if c_password == password and User.objects.get(username=username).DoesNotExist:
            us = User(username=username, email=email, password=password, first_name=fname, last_name=lname)
            us.save()
            login(request, us)  # Log in the new user
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