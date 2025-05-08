from flask import Flask, jsonify, request
from models import db, Stock
from config import Config
from flask_cors import CORS
from spotify_api import search_podcasts, get_podcast_episodes, find_show_by_title
from reddit_api import get_reddit_mentions
from youtube_api import get_youtube_buzz
# Optionally later: from sentiment_utils import analyze_sentiment_batch

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config.from_object(Config)
db.init_app(app)

@app.route("/")
def home():
    return {"message": "Welcome to the Flask API!"}

@app.route("/stocks")
def get_stocks():
    stocks = Stock.query.all()    
    return jsonify([{"symbol": s.symbol, "name": s.name} for s in stocks])

@app.route("/add-stock", methods=["POST"])
def add_stock():
    data = request.get_json()
    if not data or not 'symbol' in data or not 'name' in data:
        return {"error": "Invalid request data"}, 400

    new_stock = Stock(
        symbol=data['symbol'],
        name=data['name']
    )
    db.session.add(new_stock)
    db.session.commit()
    return {"message": f"Stock {new_stock.symbol} added successfully!"}, 201

@app.route("/search-podcast")
def search_podcast():
    query = request.args.get("q")
    if not query:
        return {"error": "Missing query parameter 'q'"}, 400

    try:
        results = search_podcasts(query)
        english_shows = [item for item in results if any(lang in ["en", "en-US"] for lang in item.get("languages", []))]
        sorted_shows = sorted(english_shows, key=lambda x: x.get("total_episodes", 0), reverse=True)        
        top_20 = sorted_shows[:25]

        podcasts = [
            {
                "name": item["name"],
                "publisher": item["publisher"],
                "description": item["description"],
                "image": item["images"][0]["url"] if item["images"] else None,
                "id": item["id"],
                "url": item["external_urls"]["spotify"],
                "episodes": item["total_episodes"],
                "languages": item.get("languages", [])
            }
            for item in top_20  
        ]
        return jsonify(podcasts)
    except Exception as e:
        return {"error": str(e)}, 500
    
from spotify_api import get_podcast_episodes

@app.route("/podcast-episodes")
def podcast_episodes():
    show_id = request.args.get("show_id")
    if not show_id:
        return {"error": "Missing required parameter 'show_id'"}, 400

    try:
        episodes = get_podcast_episodes(show_id)
        result = [
            {
                "name": ep["name"],
                "description": ep["description"],
                "release_date": ep["release_date"],
                "duration_ms": ep["duration_ms"],
                "url": ep["external_urls"]["spotify"],
                "audio_preview_url": ep.get("audio_preview_url"),
                "image": ep["images"][0]["url"] if ep.get("images") else None
            }
            for ep in episodes
        ]
        return jsonify(result)
    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route("/podcast-episodes-by-title")
def podcast_episodes_by_title():
    title = request.args.get("show_title")
    if not title:
        return {"error": "Missing required parameter 'title'"}, 400

    try:
        show = find_show_by_title(title)
        if not show:
            return {"error": f"No show found with title '{title}'"}, 404

        show_id = show["id"]
        episodes = get_podcast_episodes(show_id)

        result = [
            {
                "show_name": show["name"],
                "name": ep["name"],
                "description": ep["description"],
                "release_date": ep["release_date"],
                "duration_ms": ep["duration_ms"],
                "url": ep["external_urls"]["spotify"],
                "audio_preview_url": ep.get("audio_preview_url"),
                "image": ep["images"][0]["url"] if ep.get("images") else None
            }
            for ep in episodes
        ]
        return jsonify(result)
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/podcast-sentiment")
def podcast_sentiment():
    query = request.args.get("q")
    days = int(request.args.get("days", 30))  # default to 30 days

    if not query:
        return jsonify({"error": "Missing required query parameter: 'q' (podcast name)"}), 400

    try:
        # Get filtered Reddit mentions
        mentions = get_reddit_mentions(query, days_back=days)

        # (Optional future step)
        # sentiment_scores = analyze_sentiment_batch([m["text"] for m in mentions])
        # avg_sentiment = round(sum(sentiment_scores) / len(sentiment_scores), 3) if sentiment_scores else None

        return jsonify({
            "podcast": query,
            "days_lookback": days,
            "mention_count": len(mentions),
            # "average_sentiment": avg_sentiment,
            "mentions": mentions
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/youtube-buzz")
def youtube_buzz():
    channel_name = request.args.get("q")
    max_results = int(request.args.get("limit", 5))

    if not channel_name:
        return {"error": "Missing required query parameter: 'q'"}, 400

    try:
        data = get_youtube_buzz(channel_name, max_results=max_results)
        return jsonify(data)
    except ValueError as ve:
        return {"error": str(ve)}, 404
    except Exception as e:
        return {"error": f"Failed to fetch data: {str(e)}"}, 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
