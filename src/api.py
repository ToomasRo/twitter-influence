from fastapi import FastAPI
import pandas as pd
import uvicorn
from .get_5_latest import get_latest_top_posts
import json
from .summary_generator import generate_summary, generate_multiple_summaries


scraped_data_json = "./data/scraped_data.json"

top_users_df = pd.read_csv("./data/reputation_data.csv")
app = FastAPI(
    title="Crypto Twitter Influence API",
    description="""
    An API for analyzing crypto Twitter debates and user reputation.
    This API provides endpoints to:
    - Get top users by reputation and debate quality
    - Retrieve and summarize crypto-related debates
    - Fetch latest posts from specific users
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
with open(scraped_data_json) as f:
    scraped = json.load(f)
    # TODO make it work for every coin
    # scraped = filter(lambda x: x["ticker"] == "BTC", scraped)
    # tweets = []
    # for el in scraped:
    #     tweets += el["tweets"]
    # scraped = tweets


@app.get("/top_users")
def get_top_users(n: int = 5):
    """
    Retrieves the top N users ranked by their reputation score.
    
    The reputation score is calculated based on:
    - Quality of their crypto-related discussions
    - Engagement from other reputable users
    - Overall influence in the crypto community
    
    Parameters:
    - n: Number of top users to return (default: 5)
    
    Returns:
    - List of users containing:
        - author: Twitter username
        - reputation: Numerical reputation score
        - debate_quality: Score indicating the quality of user's debates
    """
    return (
        top_users_df.sort_values("reputation", ascending=False)
        .head(n)
        .to_dict(orient="records")
    )


@app.get("/best_debate")
def get_best_debate(n: int = 5):
    """
    Retrieves the top N users ranked by their debate quality score.
    
    The debate quality score considers:
    - Use of factual information
    - Coherence of arguments
    - Engagement in constructive discussions
    - Avoidance of toxic behavior
    
    Parameters:
    - n: Number of top users to return (default: 5)
    
    Returns:
    - List of users containing:
        - author: Twitter username
        - reputation: Overall reputation score
        - debate_quality: Score specifically for debate quality
    """
    return (
        top_users_df.sort_values("debate_quality", ascending=False)
        .head(n)
        .to_dict(orient="records")
    )


from datetime import datetime


@app.get("/summarize_debate")
def summarize_debate(u: str = "latest"):
    """
    Creates a comprehensive summary of crypto debates on Twitter.
    
    This endpoint analyzes Twitter discussions and generates an AI-powered
    summary that captures the key points, arguments, and consensus from
    the debate.
    
    Parameters:
    - u: Username to focus on for the debate summary. Use 'latest' to 
         summarize the most recent debates (default: 'latest')
    
    Returns:
    - A summary object containing:
        - text: The generated summary of the debate
    
    Note: The summary considers the reputation of participating users
    to weigh different viewpoints appropriately.
    """
    global scraped
    ticker = scraped[0]["ticker"]
    # TODO make it use this
    # if u == "latest":
    #     tweet = scraped[0]["tweets"][-1]
    # else:
    #     tweets = list(filter(lambda x: x["user"]["username"] == u, scraped))
    #     tweets_sorted = sorted(
    #         tweets,
    #         key=lambda x: datetime.strptime(x["created_at"], "%a %b %d %H:%M:%S %z %Y"),
    #         reverse=False,
    #     )
    #     tweet = tweets_sorted[-1]
    # # enrich the the usernames with reputation
    # for reply in tweet["replies"]:
    #     matching_users = top_users_df[top_users_df["author"] == reply["username"]]
    #     if not matching_users.empty:
    #         reply["reputation"] = matching_users["reputation"].values[0]
    #     else:
    #         reply["reputation"] = -1  # Default value for users not in database
    
    # matching_usersauthor = top_users_df[top_users_df["author"] == reply["username"]]
    # if not matching_usersauthor.empty:
    #     tweet["reputation"] = matching_usersauthor["reputation"].values[0]
    # else:
    #     tweet["reputation"] = -1

    # TODO send to openai to put it together.
    summary = generate_summary(ticker)
    larger_summary = generate_multiple_summaries(ticker)
    return {"text": larger_summary}


@app.get("/latest_posts/{username}",
         tags=["Posts"],
         summary="Get Latest Posts by Username",
         description="Retrieves the most recent crypto-related posts from a specific Twitter user.")
def get_latest_posts(username: str):
    """
    Fetches and returns the most recent Twitter posts from a specified user.
    
    This endpoint focuses on crypto-related content and provides context
    about the user's reputation and debate quality where available.
    
    Parameters:
    - username: Twitter username to fetch posts for (required)
    
    Returns:
    - List of recent tweets containing:
        - text: Content of the tweet
        - username: Author of the tweet
        - created_at: Timestamp of the tweet
    
    Raises:
    - HTTPException: If there's an error fetching the tweets or if the
                    user doesn't exist
    """
    try:
        tweets = get_latest_top_posts(username)
        return tweets
    except Exception as e:
        return {"error": str(e)}
    
    # TODO enrich with summary?


@app.get("/")
def read_root():
    """
    Basic health check endpoint to monitor API availability.
    
    This endpoint can be used to:
    - Verify the API is operational
    - Check if the server is responding
    - Monitor API uptime
    
    Returns:
    - A simple hello world message indicating the API is functioning
    """
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
