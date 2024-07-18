from django.db import models
from user.models import *
from django.contrib.auth.models import User
# Create your models here.

class ExternalBankAccount(models.Model):
    for_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="customerexternalaccount", null=True)
    bank_name = models.TextField()
    bank_routing_number = models.TextField()
    bank_account_number = models.TextField()
    ach_authorized = models.BooleanField(null=True)
    processor_token = models.TextField(null=True)
    verified = models.BooleanField()

class KYC(models.Model):
    address = models.TextField()
    state = models.TextField()
    zipCode = models.TextField()
    city = models.TextField()
    ssn = models.TextField()
    dob = models.TextField()
    phone = models.TextField(null=True)
    ip_address = models.TextField()
    customer_id = models.TextField(null=True)
    for_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="knowingCustomer", null=True)
    #document verification
    needs_documents = models.BooleanField(null=True)
    documents_submitted = models.BooleanField(null=True)
    documents_verified = models.BooleanField(null=True)

class CashAccount(models.Model):
    customer_id = models.TextField(null=True)
    cash_balance = models.DecimalField(decimal_places=2, max_digits=9)
    for_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_balance")
    bank_account = models.ForeignKey(ExternalBankAccount, on_delete=models.DO_NOTHING, related_name="externalBankAccount", null=True)

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('DEP', 'Deposit'),
        ('WTH', 'Withdrawal')
    )
    deposit = 'DEP'
    withdrawal = 'WTH'
    transaction_type = models.CharField(max_length=3, choices=STATUS_CHOICES, default=None, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    date_executed = models.DateTimeField(null=True)
    for_account = models.ForeignKey(CashAccount, on_delete=models.DO_NOTHING, related_name='account')
