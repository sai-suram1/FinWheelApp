from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from requests import HTTPError
from user.models import *
from django.urls import reverse
from bank.models import *
from bank.utils import *
from bank.banking_tools import *
# Create your views here.

@login_required(login_url='/user/login')
def index(request):
    config_bank = False
    if request.method == "GET":
        if CashAccount.objects.filter(for_user=request.user).count() < 1 or ExternalBankAccount.objects.filter(for_user=request.user).count() < 1:
            config_bank = True
        if config_bank:
            return render(request, "bank/index.html", {
                "config_bank": config_bank
            })
        else:
            user_account = CashAccount.objects.get(for_user=request.user)
            return render(request, "bank/index.html", {
                "user_account": user_account,
                "config_bank": config_bank
            })

#keep for a moment -> modify to making it take SSN with the other info to create a new bank acct. 
@login_required(login_url='/user/login')
def set_up_bank(request):
    config_bank = False
    ip = request.META.get('REMOTE_ADDR')
    if request.method == "POST":
        if CashAccount.objects.filter(for_user=request.user).count() < 1 or ExternalBankAccount.objects.filter(for_user=request.user).count() < 1:
            config_bank = True
            # add area for taking an address info. 
        if config_bank:
            address = {
                "address_type": "MAILING",
                "is_primary": True,
                "street": request.POST["street"],
                "city": request.POST["city"],
                "state": request.POST["state"],
                "zip_code": request.POST["zip"],
                "country": "US"
            }
            verify = create_new_customer(request.user, request.POST["number"], address, request.POST["ssn"], request.POST["dob"], ip)
            if verify:
                user_account = CashAccount.objects.get(for_user=request.user)
                return render(request, "bank/index.html", {
                    "user_account": user_account,
                    "config_bank": config_bank
                })
            else:
                return render(request, "bank/index.html", {
                    "message": "Bank Information Provided is Invalid",
                    "config_bank": config_bank
                })
        else:
            user_account = CashAccount.objects.get(for_user=request.user)
            return render(request, "bank/index.html", {
                "user_account": user_account,
                "config_bank": config_bank
            })
        # take the customer ID and store it within the user profile
        #begin the process of KYC Verification. 

@login_required(login_url='/user/login')
def account_view(request):
    pass

@login_required(login_url='/user/login')
def card_view(request):
    pass

@login_required(login_url='/user/login')
def investment_view(request):
    pass     

@login_required(login_url='/user/login')
def transactions_view(request):
    pass

from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def hook_receiver_view(request): # KYC ONLY
    # Listens only for GET and POST requests
    # returns django.http.HttpResponseNotAllowed for other requests

    # Handle the event appropriately
    return HttpResponse('success')