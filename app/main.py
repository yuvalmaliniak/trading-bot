from fastapi import FastAPI
from db.database import Database
app = FastAPI()
db_connection_str = "mongodb://mongo:27017/"
db = Database(db_connection_str)

# Example usage
new_user = {
    "email": "test@example.com",
    "balance": 1000.0
}
user_id = db.insert_user(new_user)
print(f"Inserted user with ID: {user_id}")
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
#
