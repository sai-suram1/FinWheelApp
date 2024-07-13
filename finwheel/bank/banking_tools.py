import requests
from dotenv import *
from bank.models import *
from user.models import *
from hashlib import sha256

auth = dotenv_values("bank/.env")
print(auth)

def create_new_customer(User, phone, address_list, ssn, dob, ip_address):
    url = "https://sandbox.bond.tech/api/v0/customers/"
    kyc_user = KYC(address=address_list["street"], state=address_list["state"], zipCode=address_list["zip"], city=address_list["city"], ssn=sha256(b""+ssn).hexdigest(), dob=dob, ip_address=ip_address, phone=phone)
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
    
    print(response.json()["customer_id"])
    kyc_user.customer_id = response.json()["customer_id"]
    kyc_user.save()
    kj = CashAccount.objects.get(for_user=User)
    kj.customer_id = response.json()["customer_id"]
    kj.save()
    start_KYC(KYC, ssn)


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
        "url": "https://hostname.com/webhook/route",
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

