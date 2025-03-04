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
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}

# Load model actions from CSV file
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models/predictions_by_date.csv'))
actions_df = pd.read_csv(csv_path)

# Ensure date formatting consistency
actions_df['Date'] = pd.to_datetime(actions_df['Date']).dt.strftime('%Y-%m-%d')
actions_df['Action'] = actions_df['Action'].astype(int)
actions_dict = dict(zip(actions_df['Date'], actions_df['Action']))
print(actions_dict)


class MLTrader(Strategy):
    def initialize(self, symbol: str = "SPY", cash_at_risk: float = .5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

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
        model_action = actions_dict.get(today_str, 0)  # 1 = buy, 0 = sell
        print("date is:", today_str)
        print("result:", model_action)

        # Convert sentiment into numerical representation
        sentiment_score = 1 if sentiment == "positive" else -1

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


start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 1, 1)
broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='mlstrat', broker=broker,
                    parameters={"symbol": "SPY",
                                "cash_at_risk": .3})
strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol": "SPY", "cash_at_risk": .3}
)