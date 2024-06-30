from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
import json
from ai.utils import *
from django.views.decorators.csrf import csrf_exempt
from ai.models import *
import datetime
# Create your views here.

@login_required(login_url='/user/login')
def dashboard(request):
    ch = Chat.objects.get(for_user=request.user)
    return render(request, "ai/index.html", {
        "userChat": ch,
        "chatHistory": Chat_History.objects.filter(for_chat=ch).order_by('order')
    })

@login_required(login_url='/user/login')
@csrf_exempt
def bot_operate(request):
    if request.method == "POST":
        try:
            ch = Chat.objects.get(for_user=request.user)
            try:
                last_message_number = Chat_History.objects.filter(for_chat=ch).order_by('order')[-1].order
            except Exception:
                last_message_number = 0
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            #print(data)
            # Process the data (example: add a new key-value pair)
            try:
                processed_data = str(send_message_and_get_response(data[f"message"]))
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

            # Return a JSON response with the processed data
            x = HttpResponse(processed_data)
            return x
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON"}, status=400)
    else:
        return JsonResponse({'error': "Invalid request method"}, status=405)
    
