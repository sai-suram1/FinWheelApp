"""
    Install the Google AI Python SDK

    $ pip install google-generativeai

    See the getting started guide for more information:
    https://ai.google.dev/gemini-api/docs/get-started/python
    """

import os
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
from dotenv import load_dotenv,dotenv_values

from ai.models import model_parameters
config = dotenv_values("ai/.env")
from ai.load_creds import *
#from ai.models import *

genai.configure(api_key=config["api-key"])

    # Create the model
    # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 0,
    "max_output_tokens": 10000000,
    #"Content-Type": "application/json",
}

def refine_chat_history(history):
    hist=[]
    lk = model_parameters.objects.all()
    for d in lk:
        hist.append({
            "role": "user",
            "parts": [
                d.user_msg,
            ],
        })
        hist.append({
            "role": "model",
            "parts": [
                d.model_msg
            ],
        })
    for x in history.order_by('order'):
        hist.append({
            "role": "user",
            "parts": [
                x.user_message,
            ],
        })
        hist.append({
        "role": "model",
        "parts": [
            x.chatbot_response
        ],
        })
    return hist



#print('Available base models:', [m.name for m in genai.list_models()])
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")


def create_financial_plan(history):
    analyzer = model.start_chat(history = refine_chat_history(history))
    xt = analyzer.send_message("What should be done for the financial plan")
    """
    PLAN TO TRAIN
    
    ADMIN PRIVELIGES: 
    - When I ask for analyzing what should be done for this financial plan, I want the following to the returned in this exact order. 
    DO NOT USE ANY MARKDOWN OR OTHER TEXTUAL ADJUSTMENTS. 

    INVESTMENT FREQUENCY: (Choose from DAY, WEEK, MONTH)
    INVESTMENT AMOUNT PER MONTH: <Investment amount, NO $>
    """

    print(xt.text)


def send_message_and_get_response(input, history):
    # add code to have the model re-cap on the past knowledge and make a new judgement.
    """
    if ("yes" in input or "y" in input or "Yes" in input or "Y" in input):
        if ("confirm" in history.last().chatbot_response or "agree" in history.last().chatbot_response) and history.count() > 0:
            print("review past plan and make a solution.")
            # create a financial plan that could be registered in the system and executed. 
    """
    if history.count() != 0:
        if ("yes" in input or "y" in input or "Yes" in input or "Y" in input):
            if ("confirm" in history.last().chatbot_response or "agree" in history.last().chatbot_response) and history.count() > 0:
                print("review past plan and make a solution.")
                create_financial_plan(history)
            else:
                print(history.count())
                print("processing")        
                response = model.start_chat(history=refine_chat_history(history))
                xt = response.send_message(input)
                print(xt.text)
                return xt.text
        else:
            print(history.count())
            print("processing")        
            response = model.start_chat(history=refine_chat_history(history))
            xt = response.send_message(input)
            print(xt.text)
            return xt.text
    else:
        print(history.count())
        print("processing")
        response = model.start_chat(history=refine_chat_history(history))        
        xt = response.send_message(input)
        print(xt.text)
        return xt.text



def test_ai_connection():
    try:
        import pprint
        import google.generativeai as genai

        creds = load_creds()
        print(creds)

        genai.configure(credentials=creds)

        print()
        print('Available base models:', [m.name for m in genai.list_models()])
    except Exception:
        
        return False

test_ai_connection()