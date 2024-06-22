from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse,HttpResponse
import json
from ai.utils import *
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

@login_required(login_url='/user/login')
def dashboard(request):
    return render(request, "ai/index.html")

@login_required(login_url='/user/login')
@csrf_exempt
def bot_operate(request):
    if request.method == "POST":
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)
            print(data)
            # Process the data (example: add a new key-value pair)
            processed_data = {"message":str(send_message_and_get_response(data[f"message"]))}
            #print(processed_data)
            print("sending data back")
            # Return a JSON response with the processed data
            
            x = JsonResponse(json.dumps(processed_data), status=200, safe=False)
            return x
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON"}, status=400)
    else:
        return JsonResponse({'error': "Invalid request method"}, status=405)