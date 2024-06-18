from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
            processed_data = {**data, "processed": True, "response":send_message_and_get_response(data["value"])}
            
            # Return a JSON response with the processed data
            return JsonResponse(processed_data)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)