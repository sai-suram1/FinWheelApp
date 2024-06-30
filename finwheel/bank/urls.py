from django.urls import path
from bank.views import *
app_name = "bank"
urlpatterns = [
    path("", index, name="dashboard")
]
