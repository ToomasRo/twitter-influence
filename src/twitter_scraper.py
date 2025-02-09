import requests
import json
import datetime

import dotenv
import os

dotenv.load_dotenv()

url = "https://apis.datura.ai/twitter"
api_key = "dt_$LSO2gvfJtB6UENHrgs-SS1w0zfSKmAr1gfkbBRmTkIg"
crypto_tickers = ["BTC", "ETH", "BNB", "SRP", "TORUS"]
headers = {
    "Authorization": api_key,
    "Content-Type": "application/json"
}

### scrape twitter
### returns a json containing top 18/19 tweets
def scrape_twitter(ticker, start_date="2025-02-01", end_date="2025-02-02"):
    payload = {
        "query": ticker + " -send -address -receive",
        "sort": "Top",
        "start_date": start_date,
        "end_date": end_date,
        "lang": "en",
        "min_retweets": 1,
        "min_replies": 20,
        "min_likes": 1
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    scraped_tweets = json.loads(response.text)
    return scraped_tweets


### gets up to 20 replies associated with a certain tweet by finding tweets of matching converstation_id
### returns a list of dictionary containing replied user and the reply text
def get_replies(conversation_id, start_date="2025-02-01", end_date="2025-02-02"):
    replies = []
    payload = {
        "query": "conversation_id:" + str(conversation_id),
        "sort": "Top",
        "start_date": start_date,
        "end_date": end_date,
        "lang": "en"
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    scraped_tweets = json.loads(response.text)
    for tweet in scraped_tweets:
        reply = {"username": tweet["user"]["username"], "text": tweet["text"]}
        replies.append(reply)
    return replies


### emits unneeded data in json and adds replies for each tweet
### returns json containing list of hot tweets with their top replies
def filter_data(data, start_date="2025-02-01", end_date="2025-02-02"):
    list_of_tweets = []
    for i in range(len(data)):
        new_user_dict = {
            "id":data[i]["user"]["id"],
            "name": data[i]["user"]["name"],
            "username": data[i]["user"]["username"],
            "followers_count": data[i]["user"]["followers_count"]
        }
        new_dict = {
            "user": new_user_dict,
            "text": data[i]["text"],
            "reply_count": data[i]["reply_count"],
            "retweet_count": data[i]["retweet_count"],
            "like_count": data[i]["like_count"],
            "quote_count": data[i]["quote_count"],
            "created_at": data[i]["created_at"],
            "replies": get_replies(data[i]["conversation_id"], start_date, end_date)
        }
        list_of_tweets.append(new_dict)
    return list_of_tweets

### generats all days in 2024
### returns a list of string in format 2024-MM-DD
def generate_dates_in_2024():
    date = []
    start_date = datetime.date(2024, 1, 1)
    for i in range(366):
        day = start_date + datetime.timedelta(days=i)
        date.append(str(day))
    return date


def scrape_twitter_2024(output_file="scraped_data.json"):
    date = generate_dates_in_2024()
    all_tweets = []
    for i in range(len(date)-1):
        for ticker in crypto_tickers:
            start_date = date[i]
            end_date = date[i+1]
            scraped_data = scrape_twitter(ticker, start_date, end_date)
            filtered_scraped_data = filter_data(scraped_data, start_date, end_date)
            all_tweets.append(
                {
                    "ticker": ticker,
                    "start_date": start_date,
                    "tweets": filtered_scraped_data
                }
            )
            with open(output_file, "w") as f:
                json.dump(all_tweets, f, indent=4)
   
if __name__ == "__main__":         
    scrape_twitter_2024()
