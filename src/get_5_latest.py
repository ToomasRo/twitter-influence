import requests
import json
import datetime
from twitter_scraper import get_replies

url = "https://apis.datura.ai/twitter"
api_key = "dt_$LSO2gvfJtB6UENHrgs-SS1w0zfSKmAr1gfkbBRmTkIg"
headers = {
    "Authorization": api_key,
    "Content-Type": "application/json"
}

### scrape twitter
### returns a json containing top 18/19 tweets
def scrape_twitter(username, start_date, end_date):
    payload = {
        "query": "from:" + username + " -is:reply",
        "start_date": start_date,
        "end_date": end_date,
        "sort": "Top",
        "lang": "en",
        "is_retweet": False
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    scraped_tweets = json.loads(response.text)
    return scraped_tweets[0:5]

### emits unneeded data in json and adds replies for each tweet
### returns json containing list of hot tweets with their top replies
def filter_data(data, start_date, end_date):
    list_of_tweets = []
    for i in range(len(data)):
        new_dict = {"text": data[i]["text"], "reply_count": data[i]["reply_count"], "retweet_count": data[i]["retweet_count"], "like_count": data[i]["like_count"], "quote_count": data[i]["quote_count"], "created_at": data[i]["created_at"], "replies": get_replies(data[i]["conversation_id"], start_date, end_date)}
        list_of_tweets.append(new_dict)
    return list_of_tweets

def get_latest_top_posts(username):
    start_date = datetime.date.today() + datetime.timedelta(days=-2)
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = datetime.date.today().strftime('%Y-%m-%d')
    scraped_data = scrape_twitter(username, start_date, end_date)
    filtered_scraped_data = filter_data(scraped_data, start_date, end_date)
    return filtered_scraped_data

if __name__ == "__main__":  
    latest_top = get_latest_top_posts("AlemzadehC")
    print(latest_top)