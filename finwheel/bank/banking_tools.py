import requests
from dotenv import *

auth = dotenv_values("bank/.env")
print(auth)


"""
{
                "address_type": "MAILING",
                "is_primary": True,
                "street": "345 California Ave.",
                "street2": "Suite 600",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "12345-1234",
                "country": "US"
            }

address formatting. 
"""




def create_new_customer(first_name, last_name, middle_name, ssn, phone, country_code, email, address_list, dob):
    url = "https://sandbox.bond.tech/api/v0/customers/"

    payload = {
        "dob": dob,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "ssn": ssn,
        "phone": phone,
        "phone_country_code": country_code,
        "email": email,
        "addresses": [
            {
                "address_type": "MAILING",
                "is_primary": True,
                "street": "345 California Ave.",
                "street2": "Suite 600",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "12345-1234",
                "country": "US"
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Identity": auth["id"],
        "Authorization": auth["auth"]
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)