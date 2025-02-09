# Crypto Influencer Reputation API

DebateChain uses AI to generate feeds on the latest cryptocurrency discourse. It scrapes the latest tweets using Datura API, and historical datasets on cryptocurrency pricing data.  In a Jupyter notebook, it uses pandas to compute reputation scores for Twitter users to combine factors like community engagement with their tweets, and correlations between their tweets and the crypto market to favor users who make more accurate prediction.

DebateChain performs sentiment analysis on cleaned tweets using cardiffnlp’s twitter-roberta-base-sentiment model. It uses OpenAI’s GPT-4 to summarize debates using both the text and the reputation scores for users and for those who reply.

## Prerequisites

- Python 3.10+ (tested against 3.10.2, 3.13)
- Twitter API credentials, from datura.ai
- OpenAI’s GPT-4: an API key is needed

## Installation
1. Clone the repository:
```bash
git clone git@github.com:ToomasRo/twitter-influence.git
cd twitter-influence
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root and add:
```
DATURA_API_KEY=your_twitter_api_key
LLM_API_KEY=your_llm_api_key
```

Alternatively, copy the file `.env.EXAMPLE`, rename it to `.env` and populate the keys.
```
cp .env.EXAMPLE .env
```

## Running the Application

1. Start Redis server:
```bash
uvicorn src.api:app --reload
```
(or `python3.13 -m uvicorn src.api:app --reload`)

## API Endpoints

- `GET /top_users` - Returns a list of top users
- `GET /latest_posts/{username}` - Returns the latest posts for a specific username
- `GET /summarize_debate` - Returns a list of summaries of the latest debates happening on crypto twitter using relevance scores

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`

## Data Collection

Using Twitter API, the top 20 posts per ticker were scraped from Twitter for each day in 2024. Our chosen tickers were BTC, ETH, BNB, XRP, TORUS, and the query sent to Twitter API searched top posts for these tickers one by one while excluding posts that include the words “send”, “address”, and “receive” (This was done to exclude posts that asked for ‘likes/replies’ in trade of a chance of winning 1BTC, etc).

Then, for each of these top posts, the 20 top replies to the post were found by using Twitter API to query top posts with matching conversation ID.

These scraped daily top tweets for each ticker, containing its top replies are stored in scraped_data.json and would be updated daily in the future.

## Sentiment Analysis

For analyzing the sentiment of the tweets (in scraped_data.json), we use cardiffnlp’s twitter-roberta-base-sentiment model.If the sentiment detected in the tweet matches the market movement (ie. positive sentiment && market going up), then we give it a good score. If there is a mismatch, we give it a bad score. The same logic is applied to the reptiles, where the diverse opinions are rewarded with a good score.

## Scoring Algorithm

We use factors including the following: 
- reputation: a user’s reputation is a combination of final score given by combining norm_engagement, accuracy, and debate_quality
- norm_engagement: engagement is a normalized score for the reply_count, like_count, and retweet_count
- accuracy: taken from sentiment analysis
- debate_quality: reflects the quality and diversity of the debate, for instance no replies result in a score of 0, while higher debate_quality scores result from a larger number of replies and more vibrant debate.

Recent data are given more value than old data by using a decay factor.
The users are ranked and stored in reputation_data.csv along with their respective reputation,engagement,accuracy,debate_quality scores.

## Debate Summariser

We use Open AI’s API with GPT-4 to summarize debates on Twitter for different coins. 

First, we clean the tweets that we wish to summarize, and extract parameters that are relevant for summaries, such as the reputation scores associated with the original poster and with those who have replied. We generate custom prompts depending on the currency, instructing OpenAI to use the additional fields supplied, such as reputation scores. We make an API call to return the summary of the tweet feed.
