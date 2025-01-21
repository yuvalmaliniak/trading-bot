from pymongo import MongoClient
from bson.objectid import ObjectId
import logging
from pydantic import BaseModel, EmailStr, Field

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserModel(BaseModel):
    email: EmailStr
    balance: float = 0.0
    cash_at_risk: float = 0.0
    trade_history: list = Field(default_factory=list)
    current_holdings: dict = Field(default_factory=dict)
    profit: float = 0.0

class Database:
    def __init__(self,db_connection_str):
        self.connection_string = db_connection_str
        self.client = MongoClient(self.connection_string)
        self.db = self.client["trading_app"]
        self.users_collection = self.db["users"]
        self.users_collection.create_index("email", unique=True)

    def insert_user(self, user_data):
        try:
            validated_user = UserModel(**user_data).dict()
            result = self.users_collection.insert_one(validated_user)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting user: {e}")
            return False

    def get_user(self, _id):
        try:
            return self.users_collection.find_one({"_id": ObjectId(_id)})
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return False

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
