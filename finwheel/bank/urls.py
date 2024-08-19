from django.urls import path
from bank.views import *
app_name = "bank"
urlpatterns = [
    path("", index, name="dashboard"),
    path("set_up_bank", set_up_bank, name="setupbank"),
    path("bank_hook", hook_receiver_view, name="webhook"),
    #path("plaidverification", send_to_plaid, name="achverification"),
    path("transaction", start_transaction, name="transaction"),
    path("account_info", transactions_view, name="account_info"),
    path("order", make_order, name="order"),
    path("quote", latest_quote, name="quote"),
    path("investments", investment_view, name="investments"),
    path("cancelorder/<uuid:order_id>", cancel_order_view, name="cancel"),
    path("view_document/<str:doc_id>", view_document, name="view_document"),
    path("getportfoliomovement", take_portfolio_data, name="portfoliotracker")
]
