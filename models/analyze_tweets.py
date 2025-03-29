import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from db.database import Database
import os, time
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

def get_gemini_response(question, max_retries=5):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    for attempt in range(max_retries):
        try:
            response = model.generate_content(question)
            return response.text
        except ResourceExhausted as e:
            wait_time = 25 + attempt * 5  # exponential backoff
            print(f"⏳ Rate limited by Gemini API (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"❌ Gemini API error: {str(e)}")
            break  # for now, break on unexpected errors

    return "Neutral"  # fallback if all retries fail

def analyze_tweets(tweet):
    text = tweet["subject"]
    prompt = f"""I will need you to CLASSIFY the relation of the tweet to the stock {tweet['stock_symbol']}.
    Tweet is as follows: {text}
    You need to response ONLY in one word out of the following options:
    - Positive  (if the tweet is positive about the stock)
    - Negative  (if the tweet is negative about the stock)
    - Neutral   (if the tweet is neutral about the stock)
    For example - The tweet "Tesla new car is out there, millions are here to buy" would be classified as "Positive" for stock TSLA.
    Another example - The tweet "United States increasing tax on electric cars" would be classified as "Negative" for stock TSLA."""
    response = get_gemini_response(prompt)
    # remove \n from response if exists
    if "Positive" in response:
        response = "Positive"
    elif "Negative" in response:
        response = "Negative"
    else:
        response = "Neutral"
    # print(f"Tweet: {text}")
    # print(f"Response: {response}")
    # print("----")
    return response

if __name__ == "__main__":
    pass