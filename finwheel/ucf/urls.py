from django.urls import path
from ucf.views import *
app_name = "ucf"
urlpatterns = [
    path('', index, name="index")
]
