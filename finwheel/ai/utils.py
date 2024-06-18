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

model = genai.GenerativeModel(model_name="gemini-1.0-pro-001")

def send_message_and_get_response(input):
    response = model.start_chat(history=[])
    xt = response.send_message(input)
    return xt.text