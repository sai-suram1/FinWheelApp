from django.urls import path
from ai.views import *
app_name = "ai"
urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('bot', bot_operate, name="bot"),
    path('chatpull', sendChat, name="chatpuller"),
    path('addchat', addChat, name="addChat"),
    path('deletechat/<uuid:chatid>', deleteChat, name="deleteChat")
]
