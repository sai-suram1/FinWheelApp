from django.urls import path
from ai.views import *
app_name = "ai"
urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('bot', bot_operate, name="bot")
]
