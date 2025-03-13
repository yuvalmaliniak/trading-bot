from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from app.tradingbot import MLTrader
from alpaca_trade_api import REST
from alpaca_trade_api.rest import APIError


BASE_URL = "https://paper-api.alpaca.markets"


def validate_alpaca_creds(api_key: str, api_secret: str) -> bool:
    """Check if the given Alpaca API key and secret are valid."""
    try:
        api = REST(api_key, api_secret, BASE_URL)
        account = api.get_account()

        if account and account.status in ["ACTIVE", "APPROVED"]:
            print(f"✅ API authentication successful: Account ID {account.id}")
            return True
        else:
            print("❌ API authentication failed: Account not active.")
            return False
    except APIError as e:
        print(f"❌ API authentication failed: {e.status_code} - {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False
class User:
    def __init__(self, user_data, db,creation_date):
        try:
            self.user_data = user_data
            api_data = db.get_user_api_keys(user_data["email"])
            self.api_key = api_data["api_key"]
            self.api_secret = api_data["api_secret"]


            self.symbol = self.user_data["symbol"]
            print(f"api_key is: {self.api_key}")
            self.cash_at_risk = self.user_data["cash_at_risk"]  
            self.start_date = creation_date
            self.ALPACA_CREDS = {
                "API_KEY": self.api_key,
                "API_SECRET": self.api_secret,
                "PAPER": True
            }

            self.trading_bot = MLTrader(
                name=f'mlstrat_{self.user_data["email"]}',
                broker=Alpaca(self.ALPACA_CREDS),
                parameters={"symbol": {self.symbol}, "cash_at_risk": 0.7, "api_key": self.api_key, "api_secret": self.api_secret}
            )

        except Exception as e:
            raise Exception(f"{e}")

    def start_trading(self, start_date, end_date):
        """Starts the trading bot for this user."""
        try:
            self.trading_bot.backtest(
                YahooDataBacktesting,
                start_date,
                end_date,
                parameters={"symbol": {str(self.symbol)}, "cash_at_risk": self.cash_at_risk, "api_key": self.api_key, "api_secret": self.api_secret},
                benchmark_asset=str(self.symbol),
                name=f"{self.user_data['email']}_backtest"
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
