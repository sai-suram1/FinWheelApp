from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from requests import HTTPError
from user.models import *
from django.urls import reverse
from bank.models import *
from bank.utils import *
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

#keep for a moment
@login_required(login_url='/user/login')
def set_up_bank(request):
    config_bank = False
    if request.method == "POST":
        if CashAccount.objects.filter(for_user=request.user).count() < 1 or ExternalBankAccount.objects.filter(for_user=request.user).count() < 1:
            config_bank = True
        if config_bank:
            verify = bank_verification(request.user, request.POST["name"], request.POST["AccNum"], request.POST["RoutNum"])
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