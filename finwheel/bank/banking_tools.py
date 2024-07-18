import requests
from dotenv import *
from bank.models import *
from user.models import *
from hashlib import sha256
import datetime 
from json import JSONEncoder
from bank.plaid_tools import *

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

def create_ACH_relationship(account_id, bank_account: ExternalBankAccount, processor_token):
    import requests

    url = f"https://broker-api.sandbox.alpaca.markets/v1/accounts/{account_id}/ach_relationships"

    payload = {
        "bank_account_type": "CHECKING",
        "bank_account_number": bank_account.bank_account_number,
        "bank_routing_number": bank_account.bank_routing_number,
        "account_owner_name": f"{bank_account.for_user.first_name} {bank_account.for_user.last_name}",
        "instant": True,
        "processor_token": processor_token
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)


#import requests
"""
def start_KYC(KYC: KYC, ssn: str):
    url = f"https://sandbox.atelio.com/api/v0.1/customers/{KYC.customer_id}/verification-kyc"

    payload = {
        "program_id": "72585109-8222-4221-b15b-48e87ffed790",
        "ssn": ssn,
        "phone": KYC.phone,
        "phone_country_code": "1",
        "email": KYC.for_user.email,
        "dob": KYC.dob,
        "ip": KYC.ip_address
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Identity": auth["id"],
        "Authorization": auth["auth"]
    }

    response = requests.post(url, headers=headers)

    print(response.text)

def makeWebHooksOperate():
    url = "https://sandbox.atelio.com/api/v0.1/webhooks"

    payload = {
        "events": ["kyc.verification.document_required", "kyc.verification.error", "kyc.verification.failure", "kyc.verification.reenter_information", "kyc.verification.success", "kyc.verification.timeout", "kyc.verification.under_review"],
        "url": "https://127.0.0.1:8000/bank_hook",
        "description": "KYC state changes.",
        "version": "0.1",
        "status": "STATUS_ENABLED"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Identity": auth["id"],
        "Authorization": auth["auth"]
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)





            {
                "agreement": "options_agreement",
                "ip_address": ip_address,
                "signed_at": date_time
            }
            { "agreement": "crypto_agreement", "signed_at": date_time,"ip_address": ip_address, }
            """

#makeWebHooksOperate()