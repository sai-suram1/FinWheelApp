from django.contrib import admin
from bank.models import *
# Register your models here.
admin.site.register(Transaction)
admin.site.register(CashAccount)
admin.site.register(ExternalBankAccount)