import google.generativeai as genai
from db.database import Database

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_response(question):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(question)
    return response.text

def analyze_tweets(connection_url):
    db = Database(connection_url)
    tweets = db.get_all_tweets()
    for tweet in tweets:
        text = tweet["text"]
        prompt = f"""I will give you a tweet made by {tweet['owner']}. I will need you to CLASSIFY
        the relation of the tweet to the stock {tweet['stock_symbol']}.
        Tweet is as follows: {text}
        You need to response ONLY in one word out of the following options:
        - Positive  (if the tweet is positive about the stock)
        - Negative  (if the tweet is negative about the stock)
        - Neutral   (if the tweet is neutral about the stock)
        For example - The tweet "Tesla new car is out there, millions are here to buy" would be classified as "Positive" for stock TSLA.
        Another example - The tweet "United States increasing tax on electric cars" would be classified as "Negative" for stock TSLA."""
        response = get_gemini_response(prompt)
        print(f"Tweet: {text}")
        print(f"Response: {response}")
        print("----")
