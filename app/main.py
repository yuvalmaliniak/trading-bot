from fastapi import FastAPI
from db.database import Database
from twitter_classification import fetch_tweets_with_serpapi
app = FastAPI()
db_connection_str = "mongodb://mongo:27017/"
db = Database(db_connection_str)
twitter_results = fetch_tweets_with_serpapi("Elon Musk", "TSLA")
if not db.get_all_tweets():
    print("No news found")
else:
    db.insert_tweets(twitter_results)



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

