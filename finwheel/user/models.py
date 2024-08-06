from django.db import models
from django.contrib.auth.models import User
from bank.banking_tools import *
from bank.models import *
# Create your models here.


class FinancialPlan(models.Model):
    STATUS_CHOICES = (
        ('DAY', 'Daily'),
        ('WEEK', 'Weekly'),
        ('MONTH', 'Month'),
    )
    day, week, month = 'DAY', 'WEEK', 'MONTH'
    for_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="UsersPlan")
    recurring_deposit_amount = models.DecimalField(decimal_places=2, max_digits=9)
    recurring_deposit_frequency = models.CharField(max_length=5, choices=STATUS_CHOICES, default=None, null=True)
    last_recurring_deposit = models.DateTimeField(null=True)
    next_recurring_deposit = models.DateTimeField(null=True)
    
class StockFinancialPlan(models.Model):
    STATUS_CHOICES = (
        ('DAY', 'Daily'),
        ('WEEK', 'Weekly'),
        ('MONTH', 'Month'),
    )
    day, week, month = 'DAY', 'WEEK', 'MONTH'
    for_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="UsersStock")
    ticker = models.TextField(null=True)
    recurring_deposit_amount = models.DecimalField(decimal_places=2, max_digits=9)
    recurring_deposit_frequency = models.CharField(max_length=5, choices=STATUS_CHOICES, default=None, null=True)
    last_recurring_deposit = models.DateTimeField(null=True)
    next_recurring_deposit = models.DateTimeField(null=True)

    def save(self):
        process_order(self.ticker, "buy", "market", "gtc", cash_amt=self.recurring_deposit_amount, cash_account=CashAccount.objects.get(for_user=self.for_user))
        