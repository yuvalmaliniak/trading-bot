import sys
import os

# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api import REST
from timedelta import Timedelta
from models.finbert_model import estimate_sentiment
# from dotenv import load_dotenv
import os
import pandas as pd

# load_dotenv()
#
# API_KEY = os.getenv("API_KEY")
# API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"
#
# ALPACA_CREDS = {
#     "API_KEY": API_KEY,
#     "API_SECRET": API_SECRET,
#     "PAPER": True
# }
# List of stock symbols to process
stock_symbols = ["SPY", "AAPL"]
# Dictionary to store actions for each symbol
actions_dicts = {}

# load prediction csv for each symbol
for symbol in stock_symbols:
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../models/{symbol}_predictions.csv"))
    
    if os.path.exists(csv_path):
        actions_df = pd.read_csv(csv_path)
        actions_df['Date'] = pd.to_datetime(actions_df['Date']).dt.strftime('%Y-%m-%d')
        actions_df['Action'] = actions_df['Action'].astype(int)
        actions_dicts[symbol] = dict(zip(actions_df['Date'], actions_df['Action']))
    else:
        print(f"No predictions file found for {symbol}, skipping.")
        actions_dicts[symbol] = {}  

class MLTrader(Strategy):

    def initialize(self):
        self.symbol = self.get_parameters()["symbol"]
        self.cash_at_risk = self.get_parameters()["cash_at_risk"]
        self.sleeptime = "24H" 
        self.last_trade = None
        
        self.api = REST(base_url=BASE_URL, key_id=self.get_parameters()["api_key"], secret_key= self.get_parameters()["api_secret"])

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol,
                                 start=three_days_prior,
                                 end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()

        # Get today's action from the PPO model
        today_str = self.get_datetime().strftime('%Y-%m-%d')
        model_action = actions_dicts.get(self.symbol, {}).get(today_str, 0)  # 1 = buy, 0 = sell
        print("date is:", today_str)
        print("result:", model_action)

        # Convert sentiment into numerical representation
        if sentiment == "neutral":
            sentiment_score = 0
        elif sentiment == "positive":
            sentiment_score = 1
        else:
            sentiment_score = -1

        # Weighted decision: 70% sentiment * probability, 30% PPO model
        weighted_decision = (0.8 * float(sentiment_score) * float(probability)) + (
                    0.2 * (1 if model_action == 1 else -1))
        print(weighted_decision)

        if cash > last_price:
            if weighted_decision > 0.5:  # Buy decision
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price * 1.20,
                    stop_loss_price=last_price * .95
                )
                self.submit_order(order)
                self.last_trade = "buy"
            elif weighted_decision < -0.5:  # Sell decision
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    type="bracket",
                    take_profit_price=last_price * .8,
                    stop_loss_price=last_price * 1.05
                )
                self.submit_order(order)
                self.last_trade = "sell"


# start_date = datetime(2024, 1, 1)
# end_date = datetime(2025, 1, 1)
# broker = Alpaca(ALPACA_CREDS)
# strategy = MLTrader(name='mlstrat', broker=broker,
#                     parameters={"symbol": "SPY",
#                                 "cash_at_risk": .3})
# strategy.backtest(
#     YahooDataBacktesting,
#     start_date,
#     end_date,
#     parameters={"symbol": "SPY", "cash_at_risk": .3}
# )

if __name__ == "__main__":
    pass