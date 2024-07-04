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
model = genai.GenerativeModel(model_name="tunedModels/finwheel-ai-fhfgsm1ur15q")

def send_message_and_get_response(input):
    
    response = model.start_chat(history=[])
    xt = response.send_message(input)
    print("processing")
    print(xt.text)
    return xt.text

def test_ai_connection():
    try:
        import pprint
        import google.generativeai as genai

        creds = load_creds()

        genai.configure(credentials=creds)

        print()
        print('Available base models:', [m.name for m in genai.list_models()])
    except Exception:
        return False

test_ai_connection()