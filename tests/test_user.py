import pytest
from unittest.mock import patch, MagicMock
from alpaca_trade_api.rest import APIError
from db.database import Database
from app.user import validate_alpaca_creds, User
from lumibot.brokers import Alpaca
from app.tradingbot import MLTrader

def test_valid_alpaca_creds():
    with patch("app.user.REST.get_account") as mock_get_account:
        mock_get_account.return_value = type("MockAccount", (), {"status": "ACTIVE", "id": "12345"})

        assert validate_alpaca_creds("valid_key", "valid_secret") is True

def test_invalid_alpaca_creds():
    with patch("app.user.REST.get_account", side_effect=APIError({"status": 403, "message": "Invalid API Key"})):
        assert validate_alpaca_creds("invalid_key", "invalid_secret") is False

@pytest.fixture
def mock_db():
    db = MagicMock(spec=Database)
    db.get_user_api_keys.return_value = {"api_key": "test_key", "api_secret": "test_secret"}
    return db

@pytest.fixture
def mock_alpaca():
    """Mock the Alpaca broker to prevent real API calls."""
    with patch("app.user.Alpaca") as mock_alpaca:
        mock_instance = MagicMock()
        mock_alpaca.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_mltrader():
    """Mock MLTrader to prevent real API calls."""
    with patch("app.user.MLTrader") as mock_trader:
        mock_instance = MagicMock()
        mock_trader.return_value = mock_instance
        yield mock_instance

def test_user_initialization(mock_db, mock_alpaca, mock_mltrader):
    user_data = {
        "email": "test@example.com",
        "symbol": "AAPL",
        "cash_at_risk": 0.5
    }
    creation_date = "2025-03-01"

    user = User(user_data, mock_db, creation_date)

    assert user.api_key == "test_key"
    assert user.api_secret == "test_secret"
    assert user.symbol == "AAPL"
    assert user.cash_at_risk == 0.5
    assert user.start_date == "2025-03-01"

def test_start_trading(mock_db, mock_alpaca, mock_mltrader):
    user_data = {
        "email": "test@example.com",
        "symbol": "AAPL",
        "cash_at_risk": 0.5
    }
    creation_date = "2025-03-01"
    user = User(user_data, mock_db, creation_date)

    with patch.object(user.trading_bot, "backtest") as mock_backtest:
        user.start_trading("2025-03-01", "2025-03-10")
        mock_backtest.assert_called_once()
