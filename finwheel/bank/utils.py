from bank.models import *
from datetime import datetime
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from bank.banking_tools import *
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




from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task(from_email, recipient_list, k):
    alapca_info = get_account_info(k)
    positions = get_positions_from_account(k)

    subject = f"FinWheel Daily Update - {datetime.now().month}/{datetime.now().day}/{datetime.now().year}"
    context = {
        "receiver_name": f"{k.for_user.first_name}",
        "asset_equity": alapca_info["last_equity"],
        "positions": positions
    }
    receiver_email = k.for_user.email
    template_name = "/finwheel/bank/templates/bank/email.html"
    convert_to_html_content =  render_to_string(
        template_name=template_name,
        context=context
    )
    plain_message = strip_tags(convert_to_html_content)
    send_mail(subject, plain_message, from_email, recipient_list)


from django_celery_beat.models import PeriodicTask, CrontabSchedule
try:
    schedule = CrontabSchedule(minute='0', hour='9', day_of_week='1,6')  # Send email every day at 9 AM
    schedule.save()
except CrontabSchedule.DoesNotExist:
    schedule = CrontabSchedule.objects.get(minute='0', hour='9', day_of_week='1,6')

def create_all_email_schedules():
    for k in CashAccount.objects.all():
        task = PeriodicTask.objects.create(
            crontab=schedule,
            name='Daily Email Sending',
            task='your_app.tasks.send_email_task',
            args=['customer-service@finwheel.tech', [k.for_user.email], k],
        )

