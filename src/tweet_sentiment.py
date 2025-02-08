import re
from rapidfuzz import fuzz
from transformers import pipeline
from datetime import datetime
import json

# Define a dictionary of currencies with synonyms (full names and ticker symbols)
# add and remove as to what we want
currency_synonyms = {
    "btc": ["bitcoin", "btc"],
    "eth": ["ethereum", "eth", "ether"],
    "doge": ["dogecoin", "doge"],
    "ltc": ["litecoin", "ltc"],
    "xrp": ["ripple", "xrp"],
    "ada": ["cardano", "ada"],
}
sentiment_analyzer = pipeline(
    "sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment"
)
labels = {"label_0": "negative", "label_1": "neutral", "label_2": "positive"}


def extract_currencies(text, threshold=90):
    """
    Extracts currency names from a given text by fuzzy matching against synonyms.

    Parameters:
        text (str): The text to scan.
        threshold (int): Minimum fuzzy score (0-100) for a match.

    Returns:
        list: A list of canonical currency names found in the text.
    """
    found_currencies = set()
    # Tokenize text into words (lowercase)
    tokens = re.findall(r"\w+", text.lower())

    for currency, syn_list in currency_synonyms.items():
        for syn in syn_list:
            # Break the synonym into words (to support multi-word synonyms)
            syn_tokens = syn.split()
            n = len(syn_tokens)
            if n == 1:
                for token in tokens:
                    if fuzz.ratio(token, syn) >= threshold:
                        found_currencies.add(currency)
                        break
            else:
                # For multi-word synonyms, form n-grams from the tokens
                for i in range(len(tokens) - n + 1):
                    ngram = " ".join(tokens[i : i + n])
                    if fuzz.ratio(ngram, syn) >= threshold:
                        found_currencies.add(currency)
                        break
            if currency in found_currencies:
                break
    return list(found_currencies)


def get_sentiment(text):
    """
    Analyzes the sentiment of the given text.

    Returns:
        tuple: (label, score) where label is one of "positive", "negative", or "neutral"
               and score is the confidence score.
    """
    result = sentiment_analyzer(text)[0]
    # Normalize the label to lowercase.
    label = result["label"].lower()
    return label, result["score"]


# uglytime = sample_tweets[0]["created_at"]
# dt_object = datetime.strptime(uglytime, "%a %b %d %H:%M:%S %z %Y")
# dt_object


def process_tweet_sentiments(tweet):
    """
    Analyzes the sentiment of a tweet and its replies.

    Args:
        tweet: A dictionary representing a tweet, similar to the structure in sample_tweets.

    Returns:
        dict: A dictionary containing sentiment analysis results for each currency mentioned
              in the tweet and its replies.
    """

    tweet_text = tweet["text"]
    replies = tweet["replies"]

    currencies_mentioned = extract_currencies(tweet_text)

    currency_sentiments = {
        currency: {"positive": [], "negative": [], "neutral": []}
        for currency in currencies_mentioned
    }
    labels = {"label_0": "negative", "label_1": "neutral", "label_2": "positive"}

    for reply in replies:
        reply_text = reply["text"]
        username = reply["username"]

        reply_currencies = extract_currencies(reply_text)
        if not reply_currencies:
            reply_currencies = currencies_mentioned.copy()

        sentiment_label, score = get_sentiment(reply_text)

        for currency in reply_currencies:
            if currency in currency_sentiments:
                currency_sentiments[currency][labels[sentiment_label]].append(
                    (username, reply_text, score)
                )
            else:
                currency_sentiments[currency] = {
                    "positive": [],
                    "negative": [],
                    "neutral": [],
                }
                currency_sentiments[currency][labels[sentiment_label]].append(
                    (username, reply_text, score)
                )

    return currency_sentiments


if __name__ == "__main__":
    # Example usage (assuming sample_tweets is defined as in the provided code)
    with open("data/scraped_data.json", "r") as f:
        sample_tweets = json.load(f)

    results = process_tweet_sentiments(sample_tweets[0])
    print(results)
