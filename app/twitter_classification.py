from dotenv import load_dotenv
import os
from serpapi import GoogleSearch
from datetime import datetime

# Load environment variables
load_dotenv()
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def fetch_tweets_with_serpapi(stock_symbol):
    all_tweets = []

    # Define Twitter accounts based on stock symbol
    if stock_symbol == "AAPL":
        twitter_account_owners = ["Tim Cook"]
    elif stock_symbol == "SPY":
        twitter_account_owners = [
            "CNBC", "Bloomberg", "Jeff Bezos",
            "MarketWatch", "Jim Cramer"
        ]
    else:
        return []

    for account in twitter_account_owners:
        params = {
            "q": account + " twitter",
            "engine": "google",
            "hl": "en",
            "gl": "us",
            "api_key": SERPAPI_API_KEY
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()

            # Debugging: Print full response structure
            print("🔍 Full SerpAPI Response:", results)

            organic_results = results.get("organic_results", [])
            twitter_results = []
            print("🔍 Organic Results:", organic_results)
            for result in organic_results:
                if "x" in result.get("source", "").lower() or "twitter" in result.get("source", "").lower() or "twitter.com" in result.get("link", "").lower():
                    print("🔍 Found Twitter Results:", result)
                    twitter_results.append(result)
            # Ensure 'twitter_results' exists and is a dictionary
            if not twitter_results:
                print(f"⚠️ No 'twitter_results' found for {account}")
                continue  # Skip to the next account


            for tweet in twitter_results:
                new_tweet = {}
                if isinstance(tweet, dict):  # Ensure it's a dictionary
                    tweet.pop("thumbnail", None)  # Remove unwanted fields
                    new_tweet["owner"] = account
                    new_tweet["stock_symbol"] = stock_symbol
                    new_tweet["snippet"] = tweet.get("snippet", "⚠️ No text available")  # Handle missing text
                    new_tweet["link"] = tweet.get("link", "⚠️ No link available")
                    new_tweet["date"] = tweet.get("published_date", f"{datetime.today().strftime('%Y-%m-%d')}")
                    all_tweets.append(new_tweet)
            print("✅ Extracted Tweets:", all_tweets)

        except Exception as e:
            print(f"❌ Error fetching tweets: {e}")
            return []

    return all_tweets

if __name__ == "__main__":
    test_tweets = fetch_tweets_with_serpapi("AAPL")
    print("📢 Final Extracted Tweets:", test_tweets)
