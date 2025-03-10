import os, glob
from db.database import Database
from dotenv import load_dotenv

load_dotenv()

def get_latest_tearsheet(email: str):
    """Find the latest tearsheet HTML file for the user."""
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs/"))
    search_pattern = os.path.join(logs_dir, f"{email}_backtest_*.html")

    # Get list of matching files, sorted by modification time (newest first)
    files = sorted(glob.glob(search_pattern), key=os.path.getmtime, reverse=True)

    if files:
        return files[0]
    return None
