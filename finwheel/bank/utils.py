def bank_verification(User, BankName, AccountNum, RoutingNum):
    pass

import requests
from dotenv import *


auth = dotenv_values("bank/.env")
print(auth)
def verifyAPI():
    url = f"https://sandbox.bond.tech/api/v0.1/auth/key/{auth['id']}"

    payload = {}
    headers = {
    'Identity': auth["id"],
    'Authorization': auth["auth"]
    }

    response = requests.request("GET", url, headers=headers, data = payload)
    print(response.status_code)
    return response.status_code

if verifyAPI() != 200:
    exit()

