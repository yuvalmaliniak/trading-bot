from openai import api_key
from alpaca_trade_api import REST 
from db.database import Database
from lumibot.brokers import Alpaca
from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from app.tradingbot import MLTrader
BASE_URL = "https://paper-api.alpaca.markets"

class User:
    def __init__(self, user_data, db,creation_date):
        try:
            self.user_data = user_data
            api_data = db.get_user_api_keys(user_data["email"])
            self.api_key = api_data["api_key"]
            self.api_secret = api_data["api_secret"]
            print(f"api_key is: {self.api_key}")
            self.cash_at_risk = self.user_data["cash_at_risk"]  
            self.start_date = creation_date
            self.ALPACA_CREDS = {
                "API_KEY": self.api_key,
                "API_SECRET": self.api_secret,
                "PAPER": True
            }

            self.trading_bot = MLTrader(
                name='mlstrat',
                broker=Alpaca(self.ALPACA_CREDS),
                parameters={"symbol": "SPY", "cash_at_risk": 0.7, "api_key": self.api_key, "api_secret": self.api_secret}   
            )
            print(self.trading_bot.get_parameters())

        except Exception as e:
            raise Exception(f"Error initializing user: {e}")

    def start_trading(self, start_date, end_date):
        """Starts the trading bot for this user."""
        try:
            self.trading_bot.backtest(
                YahooDataBacktesting,
                start_date,
                end_date,
                parameters={"symbol": "SPY", "cash_at_risk": self.cash_at_risk, "api_key": self.api_key, "api_secret": self.api_secret},
            )
            # self.trading_bot.backtest(
            #     YahooDataBacktesting,
            #     start_date,
            #     end_date,
            #     parameters={"symbol": "SPY", "cash_at_risk": self.cash_at_risk}
            # )

            print(f"Trading started for {self.user_data['email']}")
        except Exception as e:
            print(f"Error starting trading bot for {self.user_data['email']}: {e}")
