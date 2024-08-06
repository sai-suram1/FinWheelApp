from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
import json
import threading
from django.urls import reverse
from ai.utils import *
from django.views.decorators.csrf import csrf_exempt
from ai.models import *
import datetime
import uuid
import markdown2
from markdown2 import Markdown
import ai.train


#thread1 = threading.Thread(target=ai.train.read_input_output,args=['finwheel/ai/training_data_finance_50000.csv'])
#thread1.start()
# Create your views here.

@login_required(login_url='/user/login')
def dashboard(request):
    ch = Chat.objects.filter(for_user=request.user).order_by('-date_created')
    chat_history = []
    markdowner = Markdown()
    chat = None
    if ch.count() > 0:
        chat = True
    else:
        chat = False
    for k in ch:
        lk = Chat_History.objects.filter(for_chat=k).order_by('order')
        chat_history.append(lk)
    print(ch.count())
    return render(request, "ai/index.html", {
        "chats": ch,
        "chatCount": len(ch),
        "chatHistory": chat_history,
        "chat": chat
    })

@login_required(login_url='/user/login')
@csrf_exempt
def bot_operate(request):
    if request.method == "POST":
        try:
            print(request.body)
            data = json.loads(request.body)
            print(data)
            if data["chat"] == "":
                ch = Chat(chat_id=uuid.uuid4(), for_user=request.user, date_created=datetime.datetime.now(), chat_name=f"New Chat - {datetime.datetime.now()}")
                ch.save()
            else:
                ch = Chat.objects.get(for_user=request.user, chat_id=data["chat"])
            try:
                last_message_number = Chat_History.objects.filter(for_chat=ch).order_by('order')[-1].order
            except Exception:
                last_message_number = 0
            # Parse the JSON data from the request body
            #print(data)
            # Process the data (example: add a new key-value pair)
            try:
                processed_data = str(send_message_and_get_response(data[f"message"], Chat_History.objects.filter(for_chat=ch).order_by('date_created'), request.user))
                print(processed_data)
                new_register = Chat_History(for_chat=ch, order=last_message_number+1, user_message=data[f"message"], chatbot_response=processed_data, date_created=datetime.datetime.now())
                new_register.save()
            except Exception as e:
                processed_data = "Sorry! I cannot seem to connect to you right now. "
                print("connection error to server")
                print(e)
                new_register = Chat_History(for_chat=ch, order=last_message_number+1, user_message=data[f"message"], chatbot_response=processed_data, date_created=datetime.datetime.now())
                new_register.save()
            print("sending data back")
            markdowner = Markdown()
            if data["chat"] == "":
                return HttpResponseRedirect(reverse("ai:dashboard"))
            # Return a JSON response with the processed data
            else:
                x = HttpResponse(markdowner.convert(processed_data))
                return x
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON"}, status=400)
    else:
        return JsonResponse({'error': "Invalid request method"}, status=405)
    
@login_required(login_url='/user/login')
@csrf_exempt
def sendChat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print(data)
            chat = Chat.objects.get(for_user=request.user, chat_id=data[f"pullID"])
            generate_text_setting = ""
            last_messages = Chat_History.objects.filter(for_chat=chat).order_by('order')
            markdowner = Markdown()
            for message in last_messages:
                generate_text_setting += f"<hr> <h4>user:</h4> {markdowner.convert(message.user_message)} | Sent: {message.date_created}<br><hr><h4>bot:</h4> {markdowner.convert(message.chatbot_response)}<br>"
            x = HttpResponse(generate_text_setting)
            return x
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON"}, status=400)
    else:
        return JsonResponse({'error': "Invalid request method"}, status=405)

@login_required(login_url='/user/login')
@csrf_exempt
def addChat(request):
    if request.method == "GET":
        try:
            chat = Chat(chat_id=uuid.uuid4(), for_user=request.user, date_created=datetime.datetime.now(), chat_name="New Chat")
            chat.save()
            return HttpResponseRedirect(reverse("ai:dashboard"))
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON"}, status=400)
    else:
        return JsonResponse({'error': "Invalid request method"}, status=405)

@login_required(login_url='/user/login')
@csrf_exempt
def deleteChat(request, chatid):
    if request.method == "GET" and request.user:
        try:
            chat = Chat.objects.get(chat_id=chatid, for_user=request.user)
            chat.delete()
            return HttpResponseRedirect(reverse("ai:dashboard"))
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON"}, status=400)
    else:
        return JsonResponse({'error': "Invalid request method"}, status=405)
    
