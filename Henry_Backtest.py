import os
import openai
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

def extract_action(text: str) -> str:
    text = text.lower()
    if "final transaction proposal: **buy**" in text:
        return "BUY"
    elif "final transaction proposal: **sell**" in text:
        return "SELL"
    elif "final transaction proposal: **hold**" in text:
        return "HOLD"
    else:
        return "UNKNOWN"


from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

os.environ["OPENAI_API_KEY"] = "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"  # your OpenRouter key
os.environ["FINHUB_API_KEY"] = "d1lq231r01qt4thhpa3gd1lq231r01qt4thhpa40"

os.environ["GOOGLE_API_KEY"] = "AIzaSyAPDkeryIb0hMp_MeKWC6mCPJmpNb2TCUA"
config = DEFAULT_CONFIG.copy()
config["max_debate_rounds"] = 1            
config["max_risk_discuss_rounds"] = 1                 # Turn off extra explanation (if respected)
config["deep_think_llm"] = "gpt-4.1-nano"  # Use a different model
config["quick_think_llm"] = "gpt-4.1-nano"  # Use a different model
ta = TradingAgentsGraph(debug=False, config=config)

decisions = []
start_date = datetime.strptime("2024-05-01", "%Y-%m-%d")
end_date = datetime.strptime("2024-05-05", "%Y-%m-%d")
prices = yf.download("NVDA", start="2024-05-01", end="2024-07-01")
market_days = prices.index.normalize().strftime("%Y-%m-%d").tolist()
tickers = ["NVDA"]
date = start_date
count = 0
for ticker in tickers:
    for date in market_days:
        print("Number: ", count)
        _, decision_text = ta.propagate(ticker, date)
        #action = extract_action(decision_text)
        decisions.append({
            "ticker": ticker,
            "date": date,
            "decision": decision_text, 
            "raw_text": decision_text})
        count+=1
        
print(decisions)



# Fetch price data

prices = prices["Close"]
prices.index = prices.index.strftime("%Y-%m-%d")  # make it string for safe matching


capital = 10000
position = 0
portfolio = []

for decision in decisions:
    date = decision["date"]
    price = prices.loc[date, "NVDA"]
    if price is None:
        continue

    if decision["decision"].lower().startswith("buy") and capital > 0:
        position = capital // price
        capital = 0
    elif decision["decision"].lower().startswith("sell") and position > 0:
        capital = position * price
        position = 0

    equity = capital + position * price
    portfolio.append({"date": date, "equity": equity})


df = pd.DataFrame(portfolio)
print(df)
df["date"] = pd.to_datetime(df["date"])

plt.plot(df["date"], df["equity"])
plt.title("Equity Curve")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.grid()
plt.show()