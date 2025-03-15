from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from db.database import Database
from app.twitter_classification import fetch_tweets_with_serpapi
from datetime import datetime, timedelta
from app.user import User, validate_alpaca_creds
import time, os
from app.reporting import get_latest_tearsheet
from models.analyze_tweets import analyze_tweets
from models.graph_data_analayze import update_data
from time import sleep
from models.test_model import test_model
app = FastAPI()
db_connection_str = "mongodb://mongo:27017/"
db = Database(db_connection_str)


@app.post("/trading/user")
async def create_account(user_data: dict):
    """Create a new user account."""
    try:
        api_key = user_data["api_key"]
        api_secret = user_data["api_secret"]

        if not api_key or not api_secret:
            raise HTTPException(status_code=400, detail="Missing API key or secret.")

        if not validate_alpaca_creds(api_key, api_secret):
            raise HTTPException(status_code=403, detail="Invalid Alpaca API credentials.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating API credentials: {str(e)}")

    # ✅ Insert user into DB
    result = db.insert_user(user_data)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # ✅ Retrieve user data from DB
    user_data = db.get_user(result)
    if not user_data:
        raise HTTPException(status_code=500, detail="User could not be retrieved after creation")

    return {"message": "User created successfully", "user_id": result}


@app.patch("/trading/settings/{id}")
async def update_settings(id: str, data: dict):
    """Allow users to update their trading settings (symbol, cash_at_risk)."""
    user = db.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = {}

    if "symbol" in data:
        updates["symbol"] = data["symbol"]
    if "cash_at_risk" in data:
        if not isinstance(data["cash_at_risk"], (int, float)) or not (0 <= data["cash_at_risk"] <= 1):
            raise HTTPException(status_code=400, detail="cash_at_risk must be a number between 0 and 1.")
        updates["cash_at_risk"] = data["cash_at_risk"]
    if "days_to_run" in data:
        if not isinstance(data["days_to_run"], int) or data["days_to_run"] <= 0:
            raise HTTPException(status_code=400, detail="days_to_run must be a positive integer.")
        updates["days_to_run"] = data["days_to_run"]

    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update.")

    updated = db.update_user(id, updates)

    if updated:
        return {"message": "Settings updated successfully", "updated_fields": updates}

    raise HTTPException(status_code=500, detail="Failed to update settings")

@app.post("/trading/trade/{id}")
async def start_trading(id: str, request: Request):
    """Start trading for an existing user."""
    user_data = db.get_user(id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        user = User(user_data, db, datetime.today())
        time.sleep(5)
        user.start_trading(datetime.today() - timedelta(days=user_data["days_to_run"]), datetime.today())
        return {
            "message": f"Trading runs successfully. Visit {request.base_url}trading/report/{user_data['email']} in your browser to view the full report",
            "user_id": id
        }


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting trading: {str(e)}")


@app.get("/trading/user/{id}")
async def get_user(id: str):
    """Retrieve user data by email."""
    user = db.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/trading/report/{email}")
async def get_user_report(email: str):
    """Return the latest HTML tearsheet file for the user."""
    latest_report = get_latest_tearsheet(email)

    if not latest_report:
        raise HTTPException(status_code=404, detail="No report available")

    return FileResponse(latest_report, media_type="text/html", filename=os.path.basename(latest_report))


@app.delete("/trading/account/{id}")
async def delete_account(id: str):
    """Delete an account."""
    deleted = db.delete_user(id)
    if deleted:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/trading/model_analyze")
async def analyze_model():
    # Get the current directory before changing, and go to models
    original_dir = os.getcwd()
    os.chdir(os.path.join(original_dir, "models"))
    """Runs daily so the model will predict today's results"""
    stock_symbols = ["SPY", "AAPL"]
    for symbol in stock_symbols:
        update_data(symbol)
    sleep(30)
    test = test_model()
    os.chdir(original_dir)
    return {"message": "Model computed successfully!"}
# -------------------- Tweets Endpoints --------------------

@app.get("/tweets/{StockSymbol}")
async def get_latest_tweets(StockSymbol: str):
    all_tweets = db.get_all_tweets()

    if StockSymbol in ["AAPL", "SPY"]:
        relevant_tweets = [tweet for tweet in all_tweets if
                           isinstance(tweet, dict) and tweet.get("stock_symbol") == StockSymbol]
        print(f"Found {len(relevant_tweets)} tweets for {StockSymbol}")
        print(f"Latest tweet date: {relevant_tweets[0].get('date', '') if relevant_tweets else 'N/A'}")

        for tweet in relevant_tweets:
            tweet_date = datetime.strptime(tweet.get("date", ""), "%Y-%m-%d")
            if tweet_date.date() == datetime.today().date():
                print(f"Tweets fetched today for {StockSymbol}, no need to fetch new.")
                return {"tweets": relevant_tweets}

        # Ensure fetch_tweets_with_serpapi returns a list of dictionaries
        tweets = fetch_tweets_with_serpapi(StockSymbol)
        print("tweets got:", tweets, "type:", type(tweets))
        # if not isinstance(tweets, list):
        #     raise HTTPException(status_code=500, detail="Error fetching tweets: Expected a list")

        updated_tweets = []
        for tweet in tweets:
            if isinstance(tweet, dict):  # Ensure tweet is a dictionary
                tweet["stock_symbol"] = StockSymbol
                tweet["LLM_classification"] = analyze_tweets(tweet)
                updated_tweets.append(tweet)
            else:
                print("⚠️ Skipping non-dictionary tweet:", tweet)

        db.insert_tweets(updated_tweets)
    else:
        tweets = db.get_all_tweets()

    if not tweets:
        raise HTTPException(status_code=404, detail="No tweets found")

    return {"tweets": tweets}
