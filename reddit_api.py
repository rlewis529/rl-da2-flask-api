import os
from datetime import datetime, timedelta
import praw
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "podcast-discovery-app")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)

def get_reddit_mentions(podcast_name: str, days_back: int = 30, limit: int = 100):
    """
    Searches Reddit submissions and comments for mentions of a podcast name.
    Only matches if the phrase (case-insensitive) appears.
    """
    matched_items = []
    cutoff_time = datetime.utcnow() - timedelta(days=days_back)
    normalized_name = podcast_name.lower().replace(" ", "")

    # Search submissions
    for submission in reddit.subreddit("all").search(podcast_name, sort="new", limit=limit, time_filter="month"):
        title = submission.title.lower()
        selftext = (submission.selftext or "").lower()
        if submission.created_utc < cutoff_time.timestamp():
            continue
        if (podcast_name.lower() in title or normalized_name in title or 
            podcast_name.lower() in selftext or normalized_name in selftext):
            matched_items.append({
                "type": "submission",
                "subreddit": str(submission.subreddit),
                "text": submission.title,
                "author": str(submission.author),
                "created_utc": int(submission.created_utc),
                "permalink": f"https://reddit.com{submission.permalink}"
            })

    # Search comments
    for comment in reddit.subreddit("all").comments(limit=limit):
        body = comment.body.lower()
        if comment.created_utc < cutoff_time.timestamp():
            continue
        if podcast_name.lower() in body or normalized_name in body:
            matched_items.append({
                "type": "comment",
                "subreddit": str(comment.subreddit),
                "text": comment.body,
                "author": str(comment.author),
                "created_utc": int(comment.created_utc),
                "permalink": f"https://reddit.com{comment.permalink}" if hasattr(comment, "permalink") else None
            })

    return matched_items
