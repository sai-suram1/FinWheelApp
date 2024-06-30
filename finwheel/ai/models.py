from django.db import models
from user.models import *
# Create your models here.
class Chat(models.Model):
    for_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user")
    chat_name = models.TextField(null=True)
    date_created = models.DateTimeField(auto_created=True)

class Chat_History(models.Model):
    for_chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="fromChat")
    date_created = models.DateTimeField(auto_created=True, null=True)
    order = models.IntegerField()
    user_message = models.TextField()
    chatbot_response = models.TextField()

