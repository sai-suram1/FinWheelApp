import requests
from dotenv import *
from bank.models import *
from user.models import *
from hashlib import sha256
import datetime 
from json import JSONEncoder

auth = dotenv_values("bank/.env")
print(auth)

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


def alpaca_account_making(User, phone, address_list, ssn, dob, ip_address):
    import requests
    date_time = f"2024-07-15T21:18:31Z"
    url = "https://broker-api.sandbox.alpaca.markets/v1/accounts"

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
            { "agreement": "crypto_agreement", "signed_at": date_time,"ip_address": ip_address, },
            {
                "agreement": "options_agreement",
                "ip_address": ip_address,
                "signed_at": date_time
            }
        ],
        "documents": [
            {
                "document_type": "identity_verification",
                "content": "/9j/Cg==",
                "mime_type": "image/jpeg"
            }
        ],
        "enabled_assets": ["us_equity", "crypto", "us_option"]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic Q0tCTVA1M0taSVc1V0JST0pUQlg6MnpsWGJncWJ3VU9xbGxFajVoeWJONnRvTGFpOE1rZVBjcUgyS09KOQ=="
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    print(response.status_code)


import requests

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


makeWebHooksOperate()

