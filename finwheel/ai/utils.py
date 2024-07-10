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
config = dotenv_values("ai/.env")
from ai.load_creds import *

genai.configure(api_key=config["api-key"])

    # Create the model
    # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 0,
    "max_output_tokens": 8192,
    #"Content-Type": "application/json",
}
#print('Available base models:', [m.name for m in genai.list_models()])
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

def send_message_and_get_response(input, history):
    # add code to have the model re-cap on the past knowledge and make a new judgement.
    if ("yes" in input or "y" in input or "Yes" in input or "Y" in input) and ("confirm" in history[-1].chatbot_message or "agree" in history[-1].chatbot_message):
        print("review past plan and make a solution.")
        # create a financial plan that could be registered in the system and executed. 
    response = model.start_chat(history=refine_chat_history(history))
    xt = response.send_message(input)
    print("processing")
    print(xt.text)
    return xt.text


def refine_chat_history(history):
    hist = []
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

def test_ai_connection():
    creds = load_creds()
    print(creds)

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