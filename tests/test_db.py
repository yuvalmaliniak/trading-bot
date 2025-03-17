import pytest
import mongomock
from db.database import Database
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId

# ✅ Mock MongoDB connection
@pytest.fixture
def mock_db():
    """Creates an in-memory mock database."""
    db_instance = Database("mongodb://localhost:27017/test_db")
    db_instance.client = mongomock.MongoClient()
    db_instance.db = db_instance.client["trading_app"]
    db_instance.users_collection = db_instance.db["users"]
    db_instance.tweets_collection = db_instance.db["tweets"]
    yield db_instance
    db_instance.client.close()


# ✅ Sample User Data
sample_user = {
    "email": "test@example.com",
    "api_key": "test_key",
    "api_secret": "test_secret",
    "cash_at_risk": 0.5,
    "symbol": "AAPL",
    "days_to_run": 90
}


# ✅ Sample Tweet Data
sample_tweet = {
    "subject": "Stock is rising",
    "date": "2025-03-10",
    "link": "https://twitter.com/example",
    "thumbnail": None,
    "snippet" : "Interesting tweet about Apple stock",
    "stock_symbol": "AAPL"
}


### 🚀 1️⃣ **Test Insert User**
def test_insert_user(mock_db):
    user_id = mock_db.insert_user(sample_user)
    assert isinstance(user_id, str)  # Ensure it's a string ObjectId
    assert mock_db.get_user(user_id)["email"] == sample_user["email"]


### 🚀 2️⃣ **Test Insert Duplicate User**
def test_insert_duplicate_user(mock_db):
    user = {"username": "testuser", "email": "test@example.com"}
    mock_db.insert_user(user)
    result = mock_db.insert_user(user)  # Insert duplicate
    assert result == False



### 🚀 3️⃣ **Test Get User by ID**
def test_get_user(mock_db):
    user_id = mock_db.insert_user(sample_user)
    user = mock_db.get_user(user_id)
    assert user["email"] == sample_user["email"]
    assert user["cash_at_risk"] == sample_user["cash_at_risk"]


### 🚀 4️⃣ **Test Update User**
def test_update_user(mock_db):
    user_id = mock_db.insert_user(sample_user)
    updated = mock_db.update_user(user_id, {"cash_at_risk": 0.7})
    assert updated is True
    assert mock_db.get_user(user_id)["cash_at_risk"] == 0.7


### 🚀 5️⃣ **Test Delete User**
def test_delete_user(mock_db):
    user_id = mock_db.insert_user(sample_user)
    deleted = mock_db.delete_user(user_id)
    assert deleted is True
    assert mock_db.get_user(user_id) == {"error": "User not found"}


### 🚀 6️⃣ **Test Insert Tweets**
def test_insert_tweets(mock_db):
    mock_db.insert_tweets([sample_tweet])
    print("Inserted tweets:", mock_db.get_all_tweets())  # Debugging
    tweets = mock_db.get_all_tweets()
    assert len(tweets) == 1
    assert tweets[0]["stock_symbol"] == "AAPL"


### 🚀 7️⃣ **Test Delete Tweet by ID**
def test_delete_tweet(mock_db):
    mock_db.insert_tweets([sample_tweet])
    tweet_id = str(mock_db.get_all_tweets()[0]["_id"])
    deleted = mock_db.delete_tweets(tweet_id)
    assert deleted is True
    assert len(mock_db.get_all_tweets()) == 0


### 🚀 8️⃣ **Test Update Tweet**
def test_update_tweet(mock_db):
    mock_db.insert_tweets([sample_tweet])
    tweet_id = str(mock_db.get_all_tweets()[0]["_id"])
    updated = mock_db.update_tweets(tweet_id, {"subject": "Stock is falling"})
    assert updated is True
    assert mock_db.get_all_tweets()[0]["subject"] == "Stock is falling"


### 🚀 9️⃣ **Test Delete All Tweets**
def test_delete_all_tweets(mock_db):
    mock_db.insert_tweets([sample_tweet, sample_tweet])
    mock_db.delete_all_tweets()
    assert len(mock_db.get_all_tweets()) == 0
