from django.db import models
from user.models import *
# Create your models here.

class ExternalBankAccount(models.Model):
    bank_name = models.TextField()
    bank_routing_number = models.TextField()
    bank_account_number = models.TextField()
    verified = models.BooleanField()

class CashAccount(models.Model):
    cash_balance = models.DecimalField(decimal_places=2, max_digits=9)
    for_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_balance")
    bank_account = models.ForeignKey(ExternalBankAccount, on_delete=models.DO_NOTHING, related_name="externalBankAccount")

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
