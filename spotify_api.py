import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
TOKEN_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"

def get_spotify_token():
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def search_podcasts(query, limit=50):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": query,
        "type": "show",
        "limit": limit
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)
    response.raise_for_status()
    return response.json()["shows"]["items"]

def get_podcast_episodes(show_id, limit=20):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"limit": limit}  # You can also add offset here for pagination

    url = f"https://api.spotify.com/v1/shows/{show_id}/episodes"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("items", [])

def find_show_by_title(title):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": title, "type": "show", "limit": 1}

    response = requests.get(SEARCH_URL, headers=headers, params=params)
    response.raise_for_status()

    shows = response.json().get("shows", {}).get("items", [])
    return shows[0] if shows else None
