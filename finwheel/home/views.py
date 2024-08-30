from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
import home.utils
from bank.models import *
from django.urls import reverse
# Create your views here.
def index(request):
    if request.user.is_authenticated:
        xt = home.utils.verify_setup(request.user)
        if xt[0] == False:
            return render(request, "home/logged_index.html",{
                "setup":xt,
            })
        elif xt[0] == True and xt[1] == True:
            return HttpResponseRedirect(reverse("bank:dashboard"))
        else:
            return render(request, "home/logged_index.html",{
                "setup":xt,
                "bank_info": CashAccount.objects.get(for_user=request.user)
            })
    else:
        return render(request, "home/index.html")

@login_required(login_url="/user/login")
def setting_view(request):
    if request.method == "GET":
        return render(request, "home/settings.html", {"user":request.user, "kyc":KYC.objects.get(for_user=request.user)})
    
@login_required(login_url="/user/login")
def account_set_password(request):
    if request.method == "POST":
        p = request.POST["password"]
        n_p = request.POST["n_password"]
        if p == request.user.password:
            request.user.password = n_p
            request.user.save()
            return HttpResponseRedirect(reverse("home:setting", args={"pass_message": "password changed"}))
        else:
            return HttpResponseRedirect(reverse("home:setting", args={"pass_message": "password changed"}))

@login_required(login_url="/user/login")
def account_set_info(request):
    if request.method == "POST":
        e = request.POST["email"]
        tel = request.POST["tel"]
        addy = request.POST["address"]
        city = request.POST["city"]
        state = request.POST["state"]
        zip = request.POST["zip"]
        d = KYC.objects.get(for_user=request.user)
        request.user.email = e
        request.user.save()
        d.phone = tel
        d.address = addy
        d.state = state
        d.zipCode = zip
        try:
            xt = home.utils.update_user(d.customer_id, request.user, email=e, phonenumber=tel, street=addy, city=city, state=state, zip=zip)
            l = xt["id"]
            d.save()
        except Exception:
            return HttpResponseRedirect(reverse("home:setting", args={"info_message": "Error with changing data"}))
        return HttpResponseRedirect(reverse("home:setting", args={"info_message": "Info Changed Successfully"}))