from fastapi import FastAPI, HTTPException
from db.database import Database
from app.twitter_classification import fetch_tweets_with_serpapi

app = FastAPI()
db_connection_str = "mongodb://localhost:27017"
db = Database(db_connection_str)


#twitter_results = fetch_tweets_with_serpapi("Elon Musk", "TSLA")
# if not db.get_all_tweets():
#     print("No news found")
# else:
#     #db.insert_tweets(twitter_results)




# -------------------- User Endpoints --------------------

@app.post("/trading/user")
async def create_account(user_data: dict):
    """Create a new user account."""
    result = db.insert_user(user_data)

    if isinstance(result, dict) and "error" in result:  # If an error message is returned
        raise HTTPException(status_code=400, detail=result["error"])

    return {"message": "User created successfully", "user_id": result}


@app.post("/trading/deposit/{id}")
async def deposit_money(id: str, data : dict):
    """Deposit money into an account."""
    user = db.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    amount = data["amount"]
    if(isinstance(amount, int) or isinstance(amount, float)):
        new_balance = user["balance"] + amount
        updated = db.update_user(id, {"balance": new_balance})

        if updated:
            return {"message": "Deposit successful", "new_balance": new_balance}
        raise HTTPException(status_code=500, detail="Deposit failed")
    else:
        raise HTTPException(status_code=400, detail="Amount should be a number")




@app.post("/trading/withdraw/{id}")
async def withdraw_money(id: str, data : dict):
    """Withdraw money from an account."""
    user = db.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    amount = data["amount"]
    if (isinstance(amount, int) or isinstance(amount, float)):
        if user["balance"] < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        new_balance = user["balance"] - amount
        updated = db.update_user(id, {"balance": new_balance})

        if updated:
            return {"message": "Withdrawal successful", "new_balance": new_balance}
        raise HTTPException(status_code=500, detail="Withdrawal failed")
    else:
        raise HTTPException(status_code=400, detail="Amount should be a number")


@app.get("/trading/balance/{id}")
async def get_balance(id: str):
    """Fetch the current account balance."""
    user = db.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"balance": user["balance"]}


@app.get("/trading/report/{id}")
async def generate_report(id: str):
    """Generate and fetch user trading reports."""
    user = db.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    report = {
        "email": user["email"],
        "balance": user["balance"],
        "cash_at_risk": user["cash_at_risk"],
        "trade_history": user["trade_history"],
        "current_holdings": user["current_holdings"],
        "profit": user["profit"],
    }
    return {"report": report}


@app.delete("/trading/account/{id}")
async def delete_account(id: str):
    """Delete an account."""
    deleted = db.delete_user(id)
    if deleted:
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


# -------------------- Tweets Endpoints --------------------

@app.get("/tweets/{StockSymbol}")
async def get_latest_tweets(StockSymbol: str):
    """Fetch the latest tweets on a stock."""
    tweets = fetch_tweets_with_serpapi("stock", StockSymbol)

    if not tweets:
        raise HTTPException(status_code=404, detail="No tweets found")

    db.insert_tweets(tweets)
    return {"tweets": tweets}


# -------------------- Test Endpoint --------------------
@app.get("/")
async def root():
    return {"message": "Hello World"}
