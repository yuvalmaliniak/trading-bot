from fastapi import FastAPI
from db.database import Database
app = FastAPI()
db_connection_str = "mongodb://mongo:27017/"
db = Database(db_connection_str)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

