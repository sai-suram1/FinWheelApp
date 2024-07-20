from django.urls import path
from bank.views import *
app_name = "bank"
urlpatterns = [
    path("", index, name="dashboard"),
    path("set_up_bank", set_up_bank, name="setupbank"),
    path("bank_hook", hook_receiver_view, name="webhook"),
    path("plaidverification", send_to_plaid, name="achverification"),
    path("transaction", start_transaction, name="transaction")
]
