import yfinance as yf

msft = yf.Ticker("MSFT")

print(msft.balance_sheet.to_string())