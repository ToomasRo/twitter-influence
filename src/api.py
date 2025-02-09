from fastapi import FastAPI
import pandas as pd
import uvicorn
from .get_5_latest import get_latest_top_posts


top_users_df = pd.read_csv("./data/reputation_data.csv")
app = FastAPI()


@app.get("/top_users")
def get_top_users(n: int = 5):

    return (
        top_users_df.sort_values("reputation", ascending=False)
        .head(n)
        .to_dict(orient="records")
    )


@app.get("/latest_posts/{username}")
def get_latest_posts(username):
    try:
        tweets = get_latest_top_posts(username)
        return tweets
    except Exception as e:
        return {"error": str(e)}


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
