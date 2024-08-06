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
from user.models import *
from ai.models import model_parameters
config = dotenv_values("ai/.env")
from ai.load_creds import *
import decimal
import datetime
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


def find_and_make_trade(user, history):
    analyzer = model.start_chat(history = refine_chat_history(history))
    xt = analyzer.send_message("What is the trade that needs to be made?")
    """
        WHEN I ASK FOR THE TRADE THAT IS NEEDED TO BE MADE
        I want the following returned in this exact order:
        DO NOT USE ANY MARKDOWN OR OTHER TEXTUAL ADJUSTMENTS. 

        TICKER: <TICKER>
        ORDER SIDE: <BUY, SELL>
        TIME IN FORCE: <day, gtc, otp>
        (gtc means "Good until Canceled" and otp means "Official Opening Price")
        QUANTITY OF SHARES: <qty>
        OR 
        AMOUNT TO INVEST: <cash_amt>
    """
    lk = xt.text.split("\n")
    investment_freq = lk[0].split(":")[1].strip()
    investment_amt = float(lk[1].split(":")[1].strip())
    #print(investment_freq)
    #print(investment_amt)
    assets = []
    print(xt.text)
    kj = xt.text.split("~")
    for p in kj:
        stuff = p.split("\n")
        #print(stuff)
        asd = {}
        for d in stuff:
            if d == '' or d == ' ':
                continue
            else:
                #print(d.split(":"))
                asd.update({d.split(":")[0]: d.split(":")[1].strip()})
        assets.append(asd)
    print(assets)
    


def create_financial_plan(user, history):
    analyzer = model.start_chat(history = refine_chat_history(history))
    xt = analyzer.send_message("What should be done for the financial plan")
    """
    PLAN TO TRAIN
    
    ADMIN PRIVELIGES: 
    - When I ask for analyzing what should be done for this financial plan, I want the following to the returned in this exact order. 
    DO NOT USE ANY MARKDOWN OR OTHER TEXTUAL ADJUSTMENTS. 

    INVESTMENT FREQUENCY: (Choose from DAY, WEEK, MONTH)
    INVESTMENT AMOUNT: <Investment amount, NO $>

    When I ask for all the assets to be invested in with the new portfolio, each asset must be listed in this exact order. 
    DO NOT USE ANY MARKDOWN OR OTHER TEXTUAL ADJUSTMENTS. 

    ASSET TICKER: <asset ticker>
    INVESTMENT FREQUENCY: (Choose from DAY, WEEK, MONTH)
    INVESTMENT AMOUNT: <Investment amount, NO $>
    ~
    """

    #print(xt.text)
    lk = xt.text.split("\n")
    investment_freq = lk[0].split(":")[1].strip()
    investment_amt = float(lk[1].split(":")[1].strip())
    #print(investment_freq)
    #print(investment_amt)
    assets = []
    xt = analyzer.send_message("What are all of the assets the user wants to invest in?")
    print(xt.text)
    kj = xt.text.split("~")
    for p in kj:
        stuff = p.split("\n")
        #print(stuff)
        asd = {}
        for d in stuff:
            if d == '' or d == ' ':
                continue
            else:
                #print(d.split(":"))
                asd.update({d.split(":")[0]: d.split(":")[1].strip()})
        assets.append(asd)
    print(assets)

    #make financial plan
    try:
        f = FinancialPlan.objects.get(for_user=user)
    except Exception:
        FinancialPlan.objects.filter(for_user=user).delete()
        f = FinancialPlan(for_user=user, recurring_deposit_amount=decimal.Decimal(investment_amt), recurring_deposit_frequency=investment_freq, last_recurring_deposit=datetime.datetime.now(), next_recurring_deposit = datetime.datetime.now()+datetime.timedelta(hours=(24*30)))
        f.save()

    for lk in assets:
        if "ASSET TICKER" in lk.keys() and "INVESTMENT FREQUENCY" in lk.keys() and ("INVESTMENT AMOUNT" in lk.keys() or "INVESTMENT AMOUNT" in lk.keys() or "INVESTMENT AMOUNT" in lk.keys()):
            try:
                stockPlan = StockFinancialPlan.objects.get(for_user=user, ticker=lk["ASSET TICKER"])
                stockPlan.recurring_deposit_frequency = lk["INVESTMENT FREQUENCY"]
                stockPlan.recurring_deposit_amount = decimal.Decimal(lk["INVESTMENT AMOUNT"])
            except StockFinancialPlan.DoesNotExist:
                stockPlan = StockFinancialPlan(for_user=user, ticker=lk["ASSET TICKER"], reccuring_deposit_amount = decimal.Decimal(lk["INVESTMENT AMOUNT"]), recurring_deposit_frequency=lk["INVESTMENT FREQUENCY"], last_recurring_deposit=datetime.datetime.now(), next_recurring_desposit=datetime.datetime.now()+datetime.timedelta(hours=(24*30)))
                stockPlan.save()
        else:
            continue
        
    
    return True

def make_action(history):
    analyzer = model.start_chat(history = refine_chat_history(history))
    sol_finder = analyzer.send_message("From this chat, what action should be executed currently?\n DO NOT USE MARKDOWN OR OTHER TEXTUAL EDITS \n - creating investment plans/portfolios \n - trading stocks/assets directly.\n- changing user settings\n- ordering money transfers between accounts.\n- analysis of SEC and Earnings Data of Assets.\n - Rebalancing Portfolios and Making changes to investment plans.")
    print(sol_finder.text)
    return sol_finder.text

def send_message_and_get_response(input, history, user):
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
                plan = make_action(history)
                if plan == "creating investment plans/portfolios":
                    lk = create_financial_plan(user, history) 
                    if lk:
                        return "Financial Plan Created Successfully"
                elif plan == "trading stocks/assets directly":
                    find_and_make_trade(user, history)
                # we have covered financial plans. We need to cover the following:
                # trading stocks/assets directly. 
                # changing user settings
                # ordering money transfers between accounts. 
                # analysis of SEC and Earnings Data of Assets. 
                # Rebalancing Portfolios and Making changes to Financial plans.
                
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