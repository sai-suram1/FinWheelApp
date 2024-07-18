from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from requests import HTTPError
from user.models import *
from django.urls import reverse
from bank.models import *
from bank.utils import *
from bank.banking_tools import *
import json
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.link_token_transactions import LinkTokenTransactions
from plaid.model.link_token_account_filters import LinkTokenAccountFilters
from plaid.model.credit_filter import CreditFilter
from plaid.model.depository_filter import DepositoryFilter
from plaid.model.depository_account_subtypes import DepositoryAccountSubtypes
from plaid.model.depository_account_subtype import DepositoryAccountSubtype
from plaid.model.credit_account_subtypes import CreditAccountSubtypes
from plaid.model.credit_account_subtype import CreditAccountSubtype
from plaid import api_client
from tests.integration.util import create_client

client = create_client()

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
            xt = check_if_account_is_verified(user_account.customer_id,ExternalBankAccount.objects.get(for_user=request.user))
            print(xt)
            if xt and user_account.bank_account.ach_authorized != True:
                return HttpResponseRedirect(reverse("bank:achverification"))
            else:
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
                "unit": request.POST["unit"],
                "country": "USA"
            }
            try:
                bank = ExternalBankAccount.objects.get(for_user=request.user)
            except ExternalBankAccount.DoesNotExist:
                bank = ExternalBankAccount(for_user=request.user, bank_name=request.POST["name"], bank_account_number=request.POST["AccNum"], bank_routing_number=request.POST["RoutNum"], verified=False)
                bank.save()
            verify = alpaca_account_making(request.user, request.POST["number"], address, request.POST["ssn"], request.POST["dob"], ip)
            if verify == 200:
                """
                config_bank = False
                user_account = CashAccount.objects.get(for_user=request.user)
                return render(request, "bank/index.html", {
                    "user_account": user_account,
                    "config_bank": config_bank
                })
                """
                return HttpResponseRedirect(reverse("bank:dashboard"))
            else:
                return render(request, "bank/index.html", {
                    "message": verify,
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

@login_required(login_url='/user/login')
def send_to_plaid(request):
    if request.method == 'GET':
        # Account filtering isn't required here, but sometimes 
        # it's helpful to see an example. 

        request = LinkTokenCreateRequest(
        user=LinkTokenCreateRequestUser(
            client_user_id='user-id',
            phone_number='+1 415 5550123'
        ),
        client_name='Personal Finance App',
        products=[plaid.Products('transactions')],
        transactions=LinkTokenTransactions(
            days_requested=730
        ),
        country_codes=[plaid.model.country_code.CountryCode('US')],
        language='en',
        webhook='https://sample-web-hook.com',
        redirect_uri='https://domainname.com/oauth-page.html',
        account_filters=LinkTokenAccountFilters(
            depository=DepositoryFilter(
            account_subtypes=DepositoryAccountSubtypes([
                DepositoryAccountSubtype('checking'),
                DepositoryAccountSubtype('savings')
            ])
            ),
            credit=CreditFilter(
            account_subtypes=CreditAccountSubtypes([
                CreditAccountSubtype('credit card')
            ])
            )
        )
        )
        # create link token
        response = client.link_token_create(request)
        link_token = response['link_token']
        return render(request, "bank/plaid.html")
    else:
        data = json.loads(request.body)
        x = CashAccount.objects.get(for_user=request.user)
        p_token = get_plaid_processor_token(account_id=x.customer_id, public_token=data["public_token"])
        k = create_ACH_relationship(account_id=x.customer_id, bank_account=x.bank_account, processor_token=p_token)
        return HttpResponseRedirect(reverse("bank:dashboard"))