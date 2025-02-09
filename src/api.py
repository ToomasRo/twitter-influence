from fastapi import FastAPI
import pandas as pd
import uvicorn
import jsonify
from get_5_latest import get_latest_top_posts

url = "https://apis.datura.ai/twitter"
api_key = "dt_$LSO2gvfJtB6UENHrgs-SS1w0zfSKmAr1gfkbBRmTkIg"
headers = {
    "Authorization": api_key,
    "Content-Type": "application/json"
}

# Example DataFrame
top_users_df = pd.DataFrame({
    "author": ["AlemzadehC", "KevinSvenson_", "invest_answers", "Mrcapitalv", "BitPaine"],
    "reputation": [19.235544663139578, 13.697349627943815, 20.51674997308669, 17.449652892768967, 19.83055281407229],
    "engagement_score": [233.45714285714286, 168.95428571428573, 263.62857142857143, 54.942852263946754, 176.42857142857142],
    "accuracy_score": [1.0, 0.8400000000000001, 1.0, 0.8, 1.0],
    "debate_quality": [5.387730227342655, 1.1637212945016202, 7.542306146680807, 5.0855709854107936, 8.234224175749421]
})

app = FastAPI()

@app.get("/top_users")
def get_top_users():
    return top_users_df.to_dict(orient="records")

@app.get("/{username}/latest_posts")
def get_latest_posts(username):
    try:
        tweets = get_latest_top_posts(username)
        return jsonify(tweets)
    except Exception as e:
        return jsonify({"error": str(e)})
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)