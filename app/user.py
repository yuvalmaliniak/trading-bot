from openai import api_key

from db.database import Database
from lumibot.brokers import Alpaca
from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
BASE_URL = "https://paper-api.alpaca.markets"

class User:
    def __init__(self, user_data, db,creation_date):
        try:
            from app.tradingbot import MLTrader
            self.user_data = user_data
            api_data = db.get_user_api_keys(user_data["email"])
            self.api_key = api_data["api_key"]
            self.api_secret = api_data["api_secret"]
            print(f"api_key is: {self.api_key}")
            self.cash_at_risk = self.user_data["cash_at_risk"]  # Default to 5% risk
            self.start_date = creation_date
            self.ALPACA_CREDS = {
                "API_KEY": self.api_key,
                "API_SECRET": self.api_secret,
                "PAPER": True
            }
            print(f"user_data: {self.user_data}")
            print(f"self :  {self}")
            self.broker = Alpaca(self.ALPACA_CREDS)
            self.trading_bot = MLTrader(
                name='mlstrat',
                broker=self.broker,
                parameters= {
                    "api_key" : self.api_key,
                    "api_secret" : self.api_secret,
                    "cash_at_risk" : self.cash_at_risk,
                },
                api = REST(
                    base_url=BASE_URL,
                    key_id=self.api_key,
                    secret_key=self.api_secret
                )
            )

        except Exception as e:
            raise Exception(f"Error initializing user: {e}")

    def start_trading(self, start_date, end_date):
        """Starts the trading bot for this user."""
        try:
            self.trading_bot.backtest(
                YahooDataBacktesting,
                start_date,
                end_date,
                parameters={"symbol": "SPY", "cash_at_risk": self.cash_at_risk}
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
