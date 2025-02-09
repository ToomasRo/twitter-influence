from fastapi import FastAPI
import pandas as pd
import uvicorn
from .get_5_latest import get_latest_top_posts
import json


top_users_df = pd.read_csv("./data/reputation_data.csv")
app = FastAPI()
with open("./data/scraped_data.json") as f:
    scraped = json.load(f)
    # TODO make it work for every coin
    scraped = filter(lambda x: x["ticker"] == "BTC", scraped)
    tweets = []
    for el in scraped:
        tweets += el["tweets"]
    scraped = tweets


@app.get("/top_users")
def get_top_users(n: int = 5):

    return (
        top_users_df.sort_values("reputation", ascending=False)
        .head(n)
        .to_dict(orient="records")
    )


@app.get("/best_debate")
def get_best_debate(n: int = 5):
    return (
        top_users_df.sort_values("debate_quality", ascending=False)
        .head(n)
        .to_dict(orient="records")
    )


from datetime import datetime


@app.get("/summarize_debate")
def summarize_debate(u: str = "latest"):
    global scraped

    if u == "latest":
        tweet = scraped["tweets"][-1]
    else:
        tweets = list(filter(lambda x: x["user"]["username"] == u, scraped))
        tweetssorted = sorted(
            tweets,
            key=lambda x: datetime.strptime(x["created_at"], "%a %b %d %H:%M:%S %z %Y"),
            reverse=False,
        )
        tweet = tweetssorted[-1]
    # enrich the the usernames with reputation
    for reply in tweet["replies"]:
        matching_users = top_users_df[top_users_df["author"] == reply["username"]]
        if not matching_users.empty:
            reply["reputation"] = matching_users["reputation"].values[0]
        else:
            reply["reputation"] = -1  # Default value for users not in database
    
    matching_usersauthor = top_users_df[top_users_df["author"] == reply["username"]]
    if not matching_usersauthor.empty:
        tweet["reputation"] = matching_usersauthor["reputation"].values[0]
    else:
        tweet["reputation"] = -1
    # TODO send to openai to put it together.
    return tweet


@app.get("/latest_posts/{username}")
def get_latest_posts(username):
    try:
        tweets = get_latest_top_posts(username)
        return tweets
    except Exception as e:
        return {"error": str(e)}
    
    # TODO enrich with summary?


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
