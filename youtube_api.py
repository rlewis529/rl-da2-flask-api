import os
import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

def get_channel_id(channel_name):
    params = {
        "part": "snippet",
        "q": channel_name,
        "type": "channel",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    response.raise_for_status()
    items = response.json().get("items", [])
    return items[0]["snippet"]["channelId"] if items else None

def get_latest_videos(channel_id, max_results=5):
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "date",
        "maxResults": max_results,
        "type": "video",
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    response.raise_for_status()
    return response.json().get("items", [])

def get_video_stats(video_ids):
    params = {
        "part": "statistics,snippet",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(YOUTUBE_VIDEOS_URL, params=params)
    response.raise_for_status()
    items = response.json().get("items", [])

    video_data = []
    total_comments = 0

    for item in items:
        stats = item["statistics"]
        snippet = item["snippet"]

        comment_count = int(stats.get("commentCount", 0))
        total_comments += comment_count

        video_data.append({
            "title": snippet.get("title"),
            "video_id": item.get("id"),
            "published_at": snippet.get("publishedAt"),
            "comment_count": comment_count
        })

    return video_data, total_comments

def get_youtube_buzz(channel_name, max_results=5):
    channel_id = get_channel_id(channel_name)
    if not channel_id:
        raise ValueError(f"No channel found for '{channel_name}'")

    latest_videos = get_latest_videos(channel_id, max_results=max_results)
    video_ids = [item["id"]["videoId"] for item in latest_videos if item.get("id", {}).get("videoId")]
    video_stats, total_comment_count = get_video_stats(video_ids)

    return {
        "channel_name": channel_name,
        "channel_id": channel_id,
        "video_count": len(video_stats),
        "total_comment_count": total_comment_count,
        "videos": video_stats
    }
