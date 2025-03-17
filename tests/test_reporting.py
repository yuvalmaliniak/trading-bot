from app.reporting import get_latest_tearsheet, analyze_transactions
import pytest
import os
import tempfile
from unittest.mock import MagicMock

@pytest.fixture
def mock_tearsheet_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_files = [
            os.path.join(temp_dir, "test_backtest_20250301.html"),
            os.path.join(temp_dir, "test_backtest_20250302.html"),
        ]
        for file in test_files:
            with open(file, "w") as f:
                f.write("Mock content")

        yield test_files




def test_analyze_transactions():
    mock_db = MagicMock()
    email = "test@example.com"

    transactions = analyze_transactions(mock_db, email)

    assert isinstance(transactions, dict)
    assert "2025-03-10" in transactions
    assert transactions["2025-03-10"] == [1, -1, 1]
