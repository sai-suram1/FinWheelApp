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
        
def get_open_orders(acct: CashAccount):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{acct.customer_id}/orders?status=open"

    headers = {"accept": "application/json", "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="}

    response = requests.get(url, headers=headers)

    print(response.text)
    return response.json()

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


def get_positions_from_account(user: CashAccount):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{user.customer_id}/positions"

    headers = {"accept": "application/json","authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="}

    response = requests.get(url, headers=headers)

    #print(response.text)
    print(response.json())
    return list(response.json())

def cancel_order(user:CashAccount, order_id):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{user.customer_id}/orders/{order_id}"

    headers = {"accept": "application/json", "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="}

    response = requests.delete(url, headers=headers)

    print(response.text)



def get_account_info(acct: CashAccount):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{acct.customer_id}/account"

    headers = {"accept": "application/json", "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="}

    response = requests.get(url, headers=headers)

    print(response.text)
    return response.json()

def get_quote(symbol):
    import requests

    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest?feed=iex"

    headers = {"accept": "application/json", "APCA-API-KEY-ID": "PKGFLKPMUCPMK13R0UQW","APCA-API-SECRET-KEY": "rWg3Ho4fnC3niaEuejw1nLgaOezN7Ve0c3ZzBMUf"}

    response = requests.get(url, headers=headers)

    print(response.text)

    return response.json()

def process_order(ticker, side, type, time, qty, cash_amt, pricept: int, cash_account: CashAccount):
    import requests
    try:
        ticker = str(ticker)
        side = str(side)
        type = str(type)
        if qty != None:
            qty = float(qty)
        if cash_amt != None:
            cash_amt = float(cash_amt)
        if pricept != None:
            pricept = int(pricept)
    except Exception as e:
        print(e)
        return False
    acct_info = dict(get_account_info(cash_account))
    print(acct_info)
    positions = get_positions_from_account(cash_account)
    quote = get_quote(ticker)["quote"]["ap"]
    buying_power = None
    cash = None
    position_qty = None
    position_exists = None
    if str(side).lower() == "buy":
        buying_power = acct_info["buying_power"]
        cash = float(acct_info["cash"])
        if qty != None:
            if (quote*qty) > cash:
                return "Order Not Executed: Not Enough Cash"
            else:
                cash_account.cash_balance -= decimal.Decimal((quote*float(qty)))
        else:
            if cash_amt > cash:
                return "Order Not Executed: Not Enough Cash"
            else:
                cash_account.cash_balance -= decimal.Decimal(float(cash_amt))
    else:
        for x in positions:
            if x["symbol"] == ticker:
                position_exists = True
                position_qty = x["qty"]
                break
        if position_exists == False or qty > position_qty:
            return "You are selling more stock than you actually have."
        else:
            cash_account.cash_balance += decimal.Decimal((quote*float(qty)))
    

    url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{cash_account.customer_id}/orders"

    payload = {
        "side": side,
        "type": str(type).lower(),
        "time_in_force": time,
        "commission_type": "notional",
        "symbol": ticker,
        "qty": qty,    
    }

    if type == "limit" or type == "stop_limit":
        payload.update({"limit_price": pricept})
    if type == "stop" or type == "stop_limit":
        payload.update({"stop_price": pricept})
    if type == "trailing_stop":
        payload.update({"trail_price": pricept})

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="
    }

    response = requests.post(url, json=payload, headers=headers)
    cash_account.save()
    if response.status_code != 200:
        return response.json()["message"]
    else: 
        print(response.text)
        return response.json()["id"]

