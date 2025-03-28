from lumibot.brokers import Alpaca
from lumibot.traders import Trader
from lumibot.backtesting import YahooDataBacktesting
from app.tradingbot import MLTrader
from alpaca_trade_api import REST
from alpaca_trade_api.rest import APIError
from multiprocessing import Process
import os
import logging

BASE_URL = "https://paper-api.alpaca.markets"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_bot(user_data, api_key, api_secret, cash_at_risk, symbol):
    alpaca_creds = {
        "API_KEY": api_key,
        "API_SECRET": api_secret,
        "PAPER": True
    }

    try:
        trading_bot = MLTrader(
            name=f'mlstrat_{user_data["email"]}',
            broker=Alpaca(alpaca_creds),
            parameters={
                "symbol": {symbol},
                "cash_at_risk": cash_at_risk,
                "api_key": api_key,
                "api_secret": api_secret
            }
        )

        trader = Trader()
        trader.add_strategy(trading_bot)
        trader.run_all()
    except Exception as e:
        logger.error(f"Bot failed to run for {user_data['email']}: {e}")


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

            print(f"Trading started for {self.user_data['email']}")
        except Exception as e:
            print(f"Error starting trading bot for {self.user_data['email']}: {e}")

    def live_trading(self,db):
        # Stop old process (if exists)
        existing_bot = db.get_bot_process(self.user_data["email"])
        if existing_bot and "pid" in existing_bot:
            try:
                os.kill(existing_bot["pid"], 9)
                print(f"Old process {existing_bot['pid']} killed for {self.user_data['email']}")
            except ProcessLookupError:
                print("Process already dead")
            db.stop_bot_process(self.user_data["email"])

        # Start new process
        process = Process(
            target=run_bot,
            args=(self.user_data, self.api_key, self.api_secret, self.cash_at_risk, self.symbol)
        )
        process.start()

        # Save process info
        db.upsert_bot_process(self.user_data["email"], process.pid, self.symbol)
        print(f"Trading started in background (process) for {self.user_data['email']}")