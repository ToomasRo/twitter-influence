# Crypto Influencer Reputation API

## Prerequisites

- Python 3.10+ (3.10.2 as tested)
- Twitter API credentials, from datura.ai

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
```bash
pip install -r requirements.txt
```


5. Set up environment variables:
Create a `.env` file in the project root and add:
```
DATURA_API_KEY=your_twitter_api_key
```
(Just copy the file `.env.EXAMPLE`, rename it to `.env` and populate it)

## Running the Application

1. Start Redis server:
```bash
uvicorn src.api:app --reload
```
(or `python3 -m uvicorn src.api:app --reload`)

## API Endpoints

- `GET /top_users` - Returns a list of top users
- `GET /latest_posts/{username}` - Returns the latest posts for a specific username

## API Documentation

Once the server is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`

## Architecture
