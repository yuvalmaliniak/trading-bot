import unittest
from db.database import Database
from bson.objectid import ObjectId

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up a test database instance and clear the collection."""
        self.db = Database("mongodb://localhost:27017/")
        self.db.users_collection.delete_many({})  # Clear the collection before tests

    def test_insert_user(self):
        """Test inserting a new user."""
        user_data = {
            "email": "testuser@example.com",
            "balance": 100.0,
            "cash_at_risk": 50.0,
            "trade_history": [],
            "current_holdings": {},
            "profit": 10.0
        }
        user_id = self.db.insert_user(user_data)
        self.assertIsNotNone(user_id, "User ID should not be None")
        inserted_user = self.db.get_user(user_id)
        self.assertIsNotNone(inserted_user, "Inserted user should exist in the database")
        self.assertEqual(inserted_user["email"], user_data["email"], "Email should match")

    def test_get_user(self):
        """Test fetching a user by ID."""
        user_data = {
            "email": "testfetch@example.com",
            "balance": 200.0,
        }
        user_id = self.db.insert_user(user_data)
        fetched_user = self.db.get_user(user_id)
        self.assertIsNotNone(fetched_user, "Fetched user should exist in the database")
        self.assertEqual(fetched_user["email"], user_data["email"], "Email should match")

    def test_update_user(self):
        """Test updating an existing user."""
        user_data = {
            "email": "testupdate@example.com",
            "balance": 300.0,
        }
        user_id = self.db.insert_user(user_data)
        update_data = {"balance": 500.0}
        update_result = self.db.update_user(user_id, update_data)
        self.assertTrue(update_result, "Update should return True")
        updated_user = self.db.get_user(user_id)
        self.assertEqual(updated_user["balance"], 500.0, "Balance should be updated")

    def test_delete_user(self):
        """Test deleting a user."""
        user_data = {
            "email": "testdelete@example.com",
            "balance": 400.0,
        }
        user_id = self.db.insert_user(user_data)
        delete_result = self.db.delete_user(user_id)
        self.assertTrue(delete_result, "Delete should return True")
        deleted_user = self.db.get_user(user_id)
        self.assertIsNone(deleted_user, "User should not exist after deletion")

    def test_get_all_users(self):
        """Test fetching all users."""
        user1 = {"email": "user1@example.com", "balance": 100.0}
        user2 = {"email": "user2@example.com", "balance": 200.0}
        self.db.insert_user(user1)
        self.db.insert_user(user2)
        all_users = self.db.get_all_users()
        self.assertEqual(len(all_users), 2, "There should be 2 users in the database")
        emails = [user["email"] for user in all_users]
        self.assertIn("user1@example.com", emails, "User1 should be in the database")
        self.assertIn("user2@example.com", emails, "User2 should be in the database")

    def tearDown(self):
        """Clean up after tests."""
        self.db.users_collection.delete_many({})  # Clear the collection after tests


if __name__ == "__main__":
    unittest.main()
