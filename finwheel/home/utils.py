from home.views import *
from bank.models import *
from user.models import *
def verify_setup(user):
    verification_list = []
    # verify the user set up everything

    # 1. Check to see if they verified their bank/info
    account = CashAccount.objects.get(for_user=user)
    if account.bank_account.verified == True:
        verification_list.append(True)
    else:
        verification_list.append(False)
    # 2. Create a financial plan with Fin
    try:
        financePlan = FinancialPlan.objects.get(for_user=user)
        verification_list.append(True)
    except Exception:
        verification_list.append(False)
    
    return verification_list

def update_user(account_id, user, email, phonenumber, street, city, state, zip):
    import requests

    url = "https://broker-api.sandbox.alpaca.markets/v1/accounts/fgds"

    payload = {
        "contact": {
            "email_address": email,
            "phone_number": f"+1{phonenumber}",
            "street_address": [street],
            "state": state,
            "city": city,
            "postal_code": zip
        },
        "trusted_contact": {
            "given_name": user.first_name,
            "family_name": user.last_name,
            "email_address": email
        }
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="
    }

    response = requests.patch(url, json=payload, headers=headers)

    print(response.text)
