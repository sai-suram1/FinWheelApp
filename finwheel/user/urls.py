from django.urls import path
from user.views import *
app_name="user"
urlpatterns = [
    path('login', login_view, name="login"),
    path('register', register_view, name="register"),
    path('logout', logout_view, name="logout")
]
