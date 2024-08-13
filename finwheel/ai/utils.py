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
from bank.banking_tools import *
from bank.models import CashAccount
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
    "temperature": 1.8,
    "top_p": 1,
    "top_k": 0,
    "max_output_tokens": 8192,
    #"Content-Type": "application/json",
}

def refine_chat_history(history, user):
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
    #assets and cash info
    cash = dict(get_account_info(acct=CashAccount.objects.get(for_user=user)))["cash"]
    hist.append({
        "role": "user",
        "parts": [
            f"THE USER'S ACCOUNT HAS ${float(cash)} in cash",
        ],
    })
    hist.append({
        "role": "model",
        "parts": [
            "I understand that the user only has this much in cash and I will ensure that his balance stays above $0.01 with any transaction he does."
        ],
    })
    assets = get_positions_from_account(user=CashAccount.objects.get(for_user=user))
    for p in assets:
        hist.append({
            "role": "user",
            "parts": [
                f"Please process this. This is one of the user's assets: {p}. \n Find the proper name of the company of which the asset is held. USE BOTH THE TICKER AND THE EXCHANGE NAME TO HELP YOU. ",
            ],
        })
        hist.append({
            "role": "model",
            "parts": [
                "I understand that the user has that asset in his portfolio. I WILL USE BOTH THE TICKER AND THE EXCHANGE NAME TO FIND THE COMPANY NAME. "
            ],
        })
    return hist



#print('Available base models:', [m.name for m in genai.list_models()])
model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config)


def find_and_make_trade(user, history):
    ana = model.start_chat(history = refine_chat_history(history, user))
    x = ana.send_message("""What is the trade that needs to be made? DO NOT USE ANY MARKDOWN OR OTHER TEXTUAL ADJUSTMENTS. 
        WHEN I ASK FOR THE TRADE THAT IS NEEDED TO BE MADE
        I want the following returned in this exact order:
        

        TICKER: <TICKER>
        ORDER SIDE: <buy, sell>
        TIME IN FORCE: <day, gtc, otp>
        TYPE: <market, limit, stop_limit, trailing_stop>
        (gtc means "Good until Canceled" and otp means "Official Opening Price")
        QUANTITY OF SHARES: <qty>
        OR 
        AMOUNT TO INVEST: <cash_amt>
        """)
    #print(x.text)
    """
        DO NOT USE ANY MARKDOWN OR OTHER TEXTUAL ADJUSTMENTS. 
        WHEN I ASK FOR THE TRADE THAT IS NEEDED TO BE MADE
        I want the following returned in this exact order:
        

        TICKER: <TICKER>
        ORDER SIDE: <BUY, SELL>
        TIME IN FORCE: <day, gtc, otp>
        (gtc means "Good until Canceled" and otp means "Official Opening Price")
        QUANTITY OF SHARES: <qty>
        OR 
        AMOUNT TO INVEST: <cash_amt>
    """
    print(x.text)
    lk = x.text.split("\n")
    print("List: "+str(lk))
    info = []
    for p in lk:
        if p == '':
            continue
        else:
            s = p.split(":")
            print(s)
            info.append({s[0].strip():s[1].strip()})
    print("Dict: "+str(info))
    print("processing order")
    if "QUANTITY OF SHARES" in x.text and "PRICEPOINT" in x.text:
        xy = process_order(ticker=info[0]["TICKER"], side=info[1]["ORDER SIDE"], type=info[3]["TYPE"], time=info[2]["TIME IN FORCE"], qty=info[4]["QUANTITY OF SHARES"], cash_account=CashAccount.objects.get(for_user=user), pricept=info[5]["PRICEPOINT"])
    elif "AMOUNT TO INVEST" in x.text and "PRICEPOINT" in x.text:
        xy = process_order(ticker=info[0]["TICKER"], side=info[1]["ORDER SIDE"], type=info[3]["TYPE"], time=info[2]["TIME IN FORCE"], cash_amt=info[4]["AMOUNT TO INVEST"], cash_account=CashAccount.objects.get(for_user=user),pricept=info[5]["PRICEPOINT"])
    elif "QUANTITY OF SHARES" in x.text and "PRICEPOINT" not in x.text:
        xy = process_order(ticker=info[0]["TICKER"], side=info[1]["ORDER SIDE"], type=info[3]["TYPE"], time=info[2]["TIME IN FORCE"], qty=info[4]["QUANTITY OF SHARES"], cash_account=CashAccount.objects.get(for_user=user),cash_amt = None, pricept=None)
    elif "AMOUNT TO INVEST" in x.text and "PRICEPOINT" not in x.text:
        xy = process_order(ticker=info[0]["TICKER"], side=info[1]["ORDER SIDE"], type=info[3]["TYPE"], time=info[2]["TIME IN FORCE"], cash_amt=info[4]["AMOUNT TO INVEST"], cash_account=CashAccount.objects.get(for_user=user), qty=None, pricept=None)

    return f"Order had been made. Order ID is: {xy}"

def create_financial_plan(user, history):
    analyzer = model.start_chat(history = refine_chat_history(history, user))
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

def get_asset_data(history, user):
    analyzer = model.start_chat(history = refine_chat_history(history, user))
    
    texts = []
    xt = ""
    while len(texts) != 2:
        xt = analyzer.send_message(""" look at the history of the conversation and return one of the following: 

        DO NOT ADD ANY TEXTUAL CHANGES. 

        EARNINGS
        INCOME_STATEMENT
        BALANCE_SHEET
        CASH_FLOW
        CURRENT_PRICE
        QUOTE

        After returning that first line, return the Stock Ticker of the stock to be analyzed. 
        DO NOT ADD ANY TEXTUAL CHANGES.""")
        print(xt.text)
        if "I understand" in xt.text:
            continue
        texts = xt.text.split("\n")
        for v in texts:
            if v == '' or v == "":
                texts.remove(v)
        print(texts)
        if len(texts) != 2:
            continue
    print(texts)
    """
    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    url = f'https://www.alphavantage.co/query?function={str(texts[0]).strip()}&symbol={str(texts[1]).strip()}&apikey={config["alpha-vantage-api"]}'
    print(url)
    r = requests.get(url)
    print(r.status_code)
    data = r.json()

    print(data)
    for x in range(5):
        try:
            final_table = analyzer.send_message(f"Within the data given, find the report the user is looking for and return that specific data. Turn that said data into a HTML table. ONLY RETURN THE HTML TABLE FOR THIS: \n {data}")
            break
        except Exception:
            continue
    """
    import yfinance as yf

    stock = yf.Ticker(str(texts[1]).strip())
    final_info = ""

    if str(texts[0]).strip() == "BALANCE_SHEET":
        final_info = stock.quarterly_balance_sheet.to_html()
    elif str(texts[0]).strip() == "CASH_FLOW":
        final_info = stock.quarterly_cashflow.to_html()
    elif str(texts[0]).strip() == "INCOME_STATEMENT":
        final_info = stock.quarterly_cashflow.to_html()
    elif str(texts[0]).strip() == "EARNINGS":
        #print(stock.get_earnings_trend())
        final_info = stock.get_earnings_dates().to_html()
    else:
        final_info = stock.info
    return final_info

def FinChatReader(query):
    import requests

    url = "https://api.finchat.io/v1/query"

    payload = {
        "query": query,
        "history": [],
        "inlineSourcing": True,
        "stream": False,
        "generateChatTitle": True,
        "generateFollowUpQuestions": True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 425c70b012164e65968182108f51df9c"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())



def make_action(history, user):
    analyzer = model.start_chat(history = refine_chat_history(history, user))
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
                plan = make_action(history, user)
                if "creating investment plans/portfolios" in plan:
                    lk = create_financial_plan(user, history) 
                    if lk:
                        return "Financial Plan Created Successfully"
                elif "trading stocks/assets directly" in plan:
                    d = find_and_make_trade(user, history)
                    if type(d) == str:
                        return d
                elif "analysis of SEC and Earnings Data of Assets" in plan:
                    ana = get_asset_data(history, user)
                    return ana
                # we have covered financial plans. We need to cover the following:
                # trading stocks/assets directly. 
                # changing user settings
                # ordering money transfers between accounts. 
                # analysis of SEC and Earnings Data of Assets. 
                # Rebalancing Portfolios and Making changes to Financial plans.
                
            else:
                print(history.count())
                print("processing")        
                response = model.start_chat(history=refine_chat_history(history, user))
                xt = response.send_message(input)
                print(xt.text)
                return xt.text
        else:
            print(history.count())
            print("processing")        
            response = model.start_chat(history=refine_chat_history(history, user))
            xt = response.send_message(input)
            print(xt.text)
            return xt.text
    else:
        print(history.count())
        print("processing")
        response = model.start_chat(history=refine_chat_history(history, user))        
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