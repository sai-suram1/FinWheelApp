from django.urls import path
from home.views import *
app_name = "home"
urlpatterns = [
    path("", index, name="dashboard"),
    path("settings", setting_view, name="setting"),
    path("set_password", account_set_password, name="set_pass"),
    path("set_user_info", account_set_info, name="set_info")
]
