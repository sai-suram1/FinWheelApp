import requests
from dotenv import *
from bank.models import *
from user.models import *
from hashlib import sha256
import datetime 
from json import JSONEncoder
from bank.plaid_tools import *
import decimal

auth = dotenv_values("bank/.env")
print(auth)
"""
def create_new_customer(User, phone, address_list, ssn, dob, ip_address):
    url = "https://sandbox.bond.tech/api/v0/customers/"
    kyc_user = KYC(address=address_list["street"], state=address_list["state"], zipCode=address_list["zip_code"], city=address_list["city"], ssn=sha256(f'{ssn}'.encode("utf-8")).hexdigest(), dob=dob, ip_address=ip_address, phone=phone)
    payload = {
        "dob": dob,
        "first_name": User.first_name,
        "last_name": User.last_name,
        "ssn": ssn,
        "phone": phone,
        "phone_country_code": "1",
        "email": User.email,
        "addresses": [
            address_list
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Identity": auth["id"],
        "Authorization": auth["auth"]
    }

    response = requests.post(url, json=payload, headers=headers)
    kyc_user.save()
    
    print(response.json())
    kyc_user.customer_id = response.json()["customer_id"]
    kyc_user.save()
    kj = CashAccount.objects.get(for_user=User)
    kj.customer_id = response.json()["customer_id"]
    kj.save()
    start_KYC(KYC, ssn)
"""

def alpaca_account_making(User: User, phone, address_list, ssn, dob, ip_address):
    import requests
    date_time = f"2024-07-15T21:18:31Z"
    url = "https://broker-api.sandbox.alpaca.markets/v1/accounts"
    kyc_user = KYC(address=address_list["street"], state=address_list["state"], zipCode=address_list["zip_code"], city=address_list["city"], ssn=sha256(f'{ssn}'.encode("utf-8")).hexdigest(), dob=dob, ip_address=ip_address, phone=phone)
    payload = {
        "contact": {
            "email_address": User.email,
            "phone_number": phone,
            "city": address_list["city"],
            "state": address_list["state"],
            "postal_code": address_list["zip_code"],
            "street_address": address_list["street"],
            "unit": address_list["unit"]
        },
        "identity": {
            "tax_id_type": "USA_SSN",
            "given_name": User.first_name,
            "family_name": User.last_name,
            "date_of_birth": dob,
            "tax_id": ssn,
            # extra stuff we need to ask lol
            "country_of_citizenship": "USA",
            "country_of_tax_residence": "USA",
            "country_of_birth": "USA",
            "funding_source": ["employment_income"]
        },
        "disclosures": {
            "is_control_person": False,
            "is_affiliated_exchange_or_finra": False,
            "is_politically_exposed": False,
            "immediate_family_exposed": False,
            "employment_status": "employed"
        },
        "trusted_contact": {
            "given_name": User.first_name,
            "family_name": User.last_name,
            "email_address": User.email,
            "street_address": [address_list["street"]],
            "city": address_list["city"],
            "state": address_list["state"],
            "postal_code": address_list["zip_code"],
            "country": "USA",
            "phone_number": phone,
        },
        "agreements": [
            { "agreement": "margin_agreement", 
            "signed_at": date_time, "ip_address": ip_address,
            },
            { "agreement": "account_agreement", "signed_at":  date_time, "ip_address": ip_address,},
            { "agreement": "customer_agreement", "signed_at": date_time, "ip_address": ip_address, },
            
        ],
        "documents": [
            {
                "document_type": "identity_verification",
                "content": "/9j/Cg==",
                "mime_type": "image/jpeg"
            }
        ],
        "enabled_assets": ["us_equity"]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    print(response.status_code)
    bank_account = ExternalBankAccount.objects.get(for_user=User)
    if response.status_code == 200:
        kyc_user.customer_id = response.json()["id"]
        kyc_user.save()
        try:
            kj = CashAccount.objects.get(for_user=User)
            bank_account = kj.bank_account
            kj.customer_id = response.json()["id"]
        except CashAccount.DoesNotExist:
            bank_account = ExternalBankAccount.objects.get(for_user=User)
            kj = CashAccount(for_user=User, cash_balance=0.00, customer_id=response.json()["id"], bank_account=bank_account)
        kj.save()
        xt = validateBank(response.json()["id"], bank_account)
        if xt.status_code == 200:
            return response.status_code
        else:
            return xt.json()["message"]
    else:
        bank_account.delete()
        return response.json()["message"]
    
def validateBank(alpaca_account_id, bank_info: ExternalBankAccount):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{alpaca_account_id}/recipient_banks"

    payload = {
        "bank_code_type": "ABA",
        "name": bank_info.bank_name,
        "bank_code": bank_info.bank_routing_number,
        "account_number": bank_info.bank_account_number
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    return response

def check_if_account_is_verified(alpaca_account_id, external_bank_account):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{alpaca_account_id}/recipient_banks"

    headers = {"accept": "application/json", "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="}

    response = requests.get(url, headers=headers)

    accounts = list(response.text)
    if response.json()[0]["status"] != "APPROVED":
        print(response.json()[0]["status"])
        return False
    else:
        external_bank_account.verified = True
        external_bank_account.save()
        return True

def create_ACH_relationship(account_id, bank_account: ExternalBankAccount):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{account_id}/ach_relationships"

    payload = {
        "bank_account_type": "CHECKING",
        "bank_account_number": bank_account.bank_account_number,
        "bank_routing_number": bank_account.bank_routing_number,
        "account_owner_name": f"{bank_account.for_user.first_name} {bank_account.for_user.last_name}",
        "instant": True,
        #"processor_token": processor_token
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    if response.status_code == 409 or response.status_code == 200:
        k = check_on_ACH_relationship(account_id)
        if k == False:
            return False
        else:
            return True
    elif response.status_code == 400:
        return False
        


def check_on_ACH_relationship(account_id):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{account_id}/ach_relationships"

    headers = {"accept": "application/json", "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="}

    response = requests.get(url, headers=headers)

    #print(response.text)
    #print(response.json())
    if response.json()[0]["status"] != "APPROVED":
        return False
    else:
        return True


def pull_ach_relationships(account_id):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{account_id}/ach_relationships"

    headers = {"accept": "application/json", "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="}

    response = requests.get(url, headers=headers)

    return response.json()[0]["id"]



def make_transaction(account: CashAccount,acc_num, amount, order):
    import requests
    print(type(amount))
    url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{account.customer_id}/transfers"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="
    }
    payload = None
    record = Transaction(amount=amount, date_executed=datetime.datetime.now(), for_account=account)
    if order == "INCOMING": # deposit
        payload = {
            "transfer_type": "ach",
            "direction": "INCOMING",
            "timing": "immediate",
            "relationship_id": pull_ach_relationships(account.customer_id),
            "amount": amount,
            "fee_payment_method": "user"
        }
        record.transaction_type = "DEP"
        account.cash_balance += decimal.Decimal(amount)
    elif order == "OUTGOING":
        record.transaction_type = "WTH"
        if account.cash_balance >= decimal.Decimal(amount):
            payload = {
                "transfer_type": "ach",
                "direction": "OUTGOING",
                "timing": "immediate",
                "relationship_id": pull_ach_relationships(account.customer_id),
                "amount": amount,
                "fee_payment_method": "user"
            }
            account.cash_balance -= decimal.Decimal(amount)
        else:
            return False
        
    
    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    print(response.status_code)
    if response.status_code != 200:
        return False
    else:
        account.save()
        record.save()
        return True


def get_account_info(user: CashAccount):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{user.customer_id}"

    headers = {"accept": "application/json", "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="}

    response = requests.get(url, headers=headers)
    print(response.json())
    return dict(response.json())

def get_positions_from_account(user: CashAccount):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{user.customer_id}/positions"

    headers = {"accept": "application/json","authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="}

    response = requests.get(url, headers=headers)

    #print(response.text)
    print(response.json())
    return dict(response.json())

def process_order(ticker, side, type, qty, pricept: int, cash_account: CashAccount):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{cash_account.customer_id}/orders"

    payload = {
        "side": side,
        "type": type,
        "time_in_force": "day",
        "commission_type": "notional",
        "symbol": "AAPL",
        "qty": qty,    
    }

    """
    "limit_price": "3.14",
        "stop_price": "3.14",
        "trail_price": "3.14",
        "trail_percent": "5.0"
    """
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)

def get_quote(symbol):
    import requests

    url = f"https://paper-api.alpaca.markets/v2/assets/{symbol}"

    headers = {"accept": "application/json", "APCA-API-KEY-ID": "PKGFLKPMUCPMK13R0UQW","APCA-API-SECRET-KEY": "rWg3Ho4fnC3niaEuejw1nLgaOezN7Ve0c3ZzBMUf"}

    response = requests.get(url, headers=headers)

    print(response.text)

    return response.json()