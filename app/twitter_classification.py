#import tweepy
from dotenv import load_dotenv
import os, requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch



# Load environment variables
load_dotenv()
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def fetch_tweets_with_serpapi(stock_symbol):
    all_tweets = []
    if stock_symbol == "AAPL":
        twitter_account_owners = ["Tim Cook"]
    elif stock_symbol == "SPY":
        twitter_account_owners = [
            "CNBC", "Bloomberg", "Yahoo Finance", "TheStreet",
            "MarketWatch", "WSJ Markets", "Stocktwits", "Jim Cramer"
        ]
    else:
        return []
    for account in twitter_account_owners:
        params = {
            "q": account + "twitter",
            "engine": "google",  # Use Google engine
            "hl": "en",          # Language: English
            "gl": "us",          # Country: US
            "api_key": SERPAPI_API_KEY
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            twitter_results = results.get("twitter_results", [])
            tweets = twitter_results['tweets']
            for tweet in tweets:
                # Remove all null fields
                tweet.pop("thumbnail", None)
                tweet['owner'] = account
                tweet['stock_symbol'] = stock_symbol
            print(tweets)
            all_tweets.extend(tweets)
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            return []
        return all_tweets
if __name__ == "__main__":
    pass

#
# def extract_media_from_tweet(url):
#     """
#     Extracts media (images/videos) from a given Twitter URL.
#
#     Args:
#         url (str): The Twitter URL of the tweet.
#
#     Returns:
#         dict: A dictionary containing media URLs or a message if no media is found.
#     """
#     try:
#         # Extract the tweet ID from the URL
#         tweet_id = url.split("/")[-1].split("?")[0]
#         if not tweet_id.isdigit():
#             return {"error": "Invalid tweet URL"}
#
#         # Use snscrape to fetch the tweet
#         tweet = next(sntwitter.TwitterTweetScraper(tweet_id).get_items(), None)
#         if not tweet:
#             return {"error": "Tweet not found"}
#
#         # Extract media URLs
#         media_urls = []
#         if tweet.media:
#             for media in tweet.media:
#                 if hasattr(media, "fullUrl"):  # Images
#                     media_urls.append(media.fullUrl)
#                 elif hasattr(media, "thumbnailUrl"):  # Videos
#                     media_urls.append(media.thumbnailUrl)
#
#         return {"media_urls": media_urls} if media_urls else {"message": "No media found in the tweet"}
#     except Exception as e:
#         return {"error": str(e)}