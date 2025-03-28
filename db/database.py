from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, Field, SecretStr
# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserModel(BaseModel):
    email: EmailStr
    api_key : SecretStr
    api_secret : SecretStr
    cash_at_risk: float = 0.0
    symbol : str = "SPY"
    days_to_run: int = 365

class Database:
    def __init__(self,db_connection_str):
        self.connection_string = db_connection_str
        self.client = MongoClient(self.connection_string)
        self.db = self.client["trading_app"]
        self.users_collection = self.db["users"]
        self.users_collection.create_index("email", unique=True)
        self.tweets_collection = self.db["tweets"]
        self.running_bots_collection = self.db["running_bots"]
        self.running_bots_collection.create_index("email", unique=True)

    def insert_user(self, user_data):
        try:
            validated_user = UserModel(**user_data).model_dump()
            validated_user["api_key"] = validated_user["api_key"].get_secret_value()
            validated_user["api_secret"] = validated_user["api_secret"].get_secret_value()
            result = self.users_collection.insert_one(validated_user)
            return str(result.inserted_id)
        except DuplicateKeyError:
            logger.error(f"Error inserting user: Duplicate email {user_data['email']}")
            return {"error": "Duplicate email. This email is already registered."}
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return False

    def get_user(self, _id):
        try:
            user = self.users_collection.find_one({"_id": ObjectId(_id)},{"_id": 0, "api_secret": 0})  # Hide API secret
            return user if user else {"error": "User not found"}
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return {"error": "Invalid user ID"}

    def get_user_api_keys(self, email):
        """
        Retrieves API key and secret for a user.
        """
        try:
            user = self.users_collection.find_one({"email": email}, {"_id": 0, "api_key": 1, "api_secret": 1})
            return user if user else {"error": "User not found"}
        except Exception as e:
            logger.error(f"Error fetching API keys: {e}")
            return {"error": "Database error"}

    def update_user(self, _id, update_data):
        try:
            result = self.users_collection.update_one(
                {"_id": ObjectId(_id)}, {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    def delete_user(self, _id):
        try:
            result = self.users_collection.delete_one({"_id": ObjectId(_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False

    def get_all_users(self):
        try:
            return list(self.users_collection.find())
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []

    def insert_tweets(self, tweets_list):
        """
        Inserts a list of tweets items into the `tweets` collection.

        :param tweets_list: List of dictionaries with keys: 'snippet', 'published_date'.
        """
        try:
            for tweet in tweets_list:
                # Calculate the actual datetime from 'hours ago'
                tweet_date = datetime.today().strftime('%Y-%m-%d')

                # Prepare the document for insertion
                tweet_document = {
                    "subject": tweet['snippet'],
                    "date": tweet_date,
                    "link": tweet.get("link"),
                    "thumbnail": tweet.get("thumbnail"),
                    "stock_symbol": tweet.get("stock_symbol"),
                }

                # Insert the document into the collection
                self.tweets_collection.insert_one(tweet_document)
            logger.info("Tweet inserted successfully.")
        except Exception as e:
            logger.error(f"Error inserting Tweets: {e}")

    def get_all_tweets(self):
        """
        Retrieves all tweets from the `tweets` collection.

        :return: List of tweets documents.
        """
        try:
            result = self.tweets_collection.delete_many({"stock_symbol": {"$exists": False}})
            tweets = list(self.tweets_collection.find())

            # Convert ObjectId to string for JSON serialization
            for tweet in tweets:
                tweet["_id"] = str(tweet["_id"])  # Convert ObjectId to string

            return tweets
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return []


    def delete_tweets(self, tweet_id):
        """
        Deletes a specific tweet item by its ObjectId.

        :param tweet_id: The ObjectId of the tweet item to delete.
        :return: True if deleted, False otherwise.
        """
        try:
            result = self.tweets_collection.delete_one({"_id": ObjectId(tweet_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting tweet: {e}")
            return False

    def update_tweets(self, tweet_id, update_data):
        """
        Updates a specific tweet item by its ObjectId.

        :param tweet_id: The ObjectId of the tweet item to update.
        :param update_data: The new data to update.
        :return: True if updated, False otherwise.
        """
        try:
            result = self.tweets_collection.update_one(
                {"_id": ObjectId(tweet_id)}, {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating tweet: {e}")
            return False

    def delete_all_tweets(self):
        """Deletes all tweets from the database."""
        result = self.tweets_collection.delete_many({})
        print(f"✅ Deleted {result.deleted_count} tweets.")

    def upsert_bot_process(self, email, pid, symbol):
        """Insert or update a running bot process for a user."""
        try:
            self.running_bots_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "pid": pid,
                        "symbol": symbol,
                        "status": "running",
                        "start_time": datetime.utcnow()
                    }
                },
                upsert=True
            )
            logger.info(f"✅ Process {pid} saved for {email}")
        except Exception as e:
            logger.error(f"Error saving bot process: {e}")

    def get_bot_process(self, email):
        """Get the process info for a specific user."""
        try:
            return self.running_bots_collection.find_one({"email": email})
        except Exception as e:
            logger.error(f"Error retrieving bot process: {e}")
            return None

    def stop_bot_process(self, email):
        """Terminate a running bot process for the user."""
        try:
            bot = self.running_bots_collection.find_one({"email": email})
            if bot and "pid" in bot:
                import os
                os.kill(bot["pid"], 9)  # Force kill
                self.running_bots_collection.delete_one({"email": email})
                logger.info(f"🛑 Process {bot['pid']} killed for {email}")
                return True
            else:
                logger.warning(f"No process found to stop for {email}")
                return False
        except Exception as e:
            logger.error(f"Error stopping bot process: {e}")
            return False

    def get_all_running_bots(self):
        """Get all running bot processes."""
        try:
            return list(self.running_bots_collection.find())
        except Exception as e:
            logger.error(f"Error fetching running bots: {e}")
            return []