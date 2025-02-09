import openai
from os import getenv
import re
import json
from .sample_tweets import chosen_tweets

# Sample data (replace this with actual JSON input)
data = {
    "user": {
        "id": "1449357111335571461",
        "name": "DrSommer.eth",
        "username": "DrSommerNFT",
        "followers_count": 4211,
    },
    "text": "Fuck it! #NewProfilePic @quirkiesnft https://t.co/ObhAjfDJVO",
    "reputation": 5,
    "reply_count": 25,
    "retweet_count": 25,
    "like_count": 130,
    "quote_count": 0,
    "created_at": "Tue Jan 02 19:52:22 +0000 2024",
    "replies": [
        {
            "username": "onefckngdingler",
            "reputation": -1,
            "text": "@DrSommerNFT @quirkiesnft Here we goooooo",
        },
        {
            "username": "theNFT_Pilot",
            "reputation": 2,
            "text": "@DrSommerNFT @quirkiesnft Grail.",
        },
        {
            "username": "mrclaudiojr",
            "text": "@DrSommerNFT @quirkiesnft More bullish on this 🤩",
        },
        {
            "username": "EgyptianCali",
            "text": "@DrSommerNFT @quirkiesnft Let’s go Sommer !!!",
        },
        {
            "username": "JanxNFT",
            "text": "@DrSommerNFT @quirkiesnft GordonGonerEffect 😁",
        },
        {
            "username": "OneAndOnlyPapii",
            "text": "@DrSommerNFT @quirkiesnft HOLY SHIT, we must be on fire hahaha lets goooo",
        },
    ],
}


# Function to clean text (remove URLs, mentions, and hashtags)
def clean_text(text):
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"@\w+", "", text)  # Remove mentions
    text = re.sub(r"#\w+", "", text)  # Remove hashtags
    return text.strip()


# Extract relevant features
main_tweet = clean_text(data["text"])
engagement = f"Likes: {data['like_count']}, Retweets: {data['retweet_count']}, Replies: {data['reply_count']}"
top_replies = [clean_text(reply["text"]) for reply in data["replies"][:5]]
reputation_summary = [
    reply["reputation"] for reply in data["replies"] if "reputation" in reply
]

# Format the input for the LLM
summary_prompt = f"""
Summarize the following Twitter conversation:

- **Main Tweet:** "{main_tweet}"
- **Engagement:** {engagement}
- **Top Replies:** {top_replies}
- **Reputation Scores:** {reputation_summary}

Summarize the sentiment, key themes, and user engagement.
"""

# Call OpenAI GPT API (Requires API key)
api_key = getenv("LLM_API_KEY")
open_ai_client = openai.OpenAI(api_key=api_key)


def get_prompt(currency="bitcoin"):
    return f"""Summarize (ideally in 4-5 lines) the key themes and engagement dynamics of this post 
    while accounting for the reputation scores assigned to respondents (with the exception that reputation of -1 simply indicates a new user). 
    Higher reputation respondents should be weighted more heavily in the summary. 
    Additionally, if given a large dataset of similar posts, rank them by their relevance 
    to the {currency} cryptocurrency market based on both textual similarity, 
    engagement-weighted reputation, and likelihood that it might correctly understand the market and recent movements."""


def generate_summary(currency="bitcoin", tweet=data):
    """
    Summary: The Twitter post is cryptic and seemingly relates to making a bold or daring decision, suggested by the phrase "Fuck it!".
    The engagement level is moderate with 130 likes and 25 retweets. The response sentiment is quite positive,
    with references to excitement, encouragement ("Here we go", "Let’s go Sommer!!!") and bullish market behavior ("More bullish on this").
    The responders have low reputation scores, meaning they aren't heavily influential within this community, except one who is a new user.
    It's challenging to directly associate this conversation with the BTC cryptocurrency market due to lack of specifics.
    """
    prompt = get_prompt(currency)
    response = open_ai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": summary_prompt},
        ],
    )
    summary = response.choices[0].message.content
    print("Summary:", summary)
    return summary


def generate_multiple_summaries(currency="bitcoin", tweets=chosen_tweets):
    summaries = [generate_summary(currency, tweet) for tweet in tweets]
    formatted_output = f"""
    Recent debates for {currency}:
    ---------------------------------------------------------
    """  # Start with user ID
    for i, summary in enumerate(summaries):
        formatted_output += summary + "\n"  # Add each summary with a newline

        if i < len(summaries) - 1:  # Add separator if not the last summary
            formatted_output += "------------------------------------------------\n\n"

    return formatted_output
