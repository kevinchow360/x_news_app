import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace with your X API Bearer Token
BEARER_TOKEN = os.environ.get("AAAAAAAAAAAAAAAAAAAAAB4i5AEAAAAAKrOouPFkj4RqB9t4oUlM23RXDVo%3DRuNCOXrvkwSjm9xStodMFEvAnq5IypMkZc1zZOubdFANuh7tWI")

def fetch_trending_posts(query, max_results=4):
    url = f"https://api.x.com/2/tweets/search/recent?query={query}&max_results={max_results}"
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    ticker = data.get("ticker")
    signal = data.get("signal")
    if not ticker or not signal:
        return jsonify({"error": "Missing ticker or signal"}), 400

    # Fetch trending posts related to the ticker
    trending_posts = fetch_trending_posts(ticker)

    return jsonify({
        "status": "success",
        "ticker": ticker,
        "signal": signal,
        "trending_posts": trending_posts,
    })

if __name__ == "__main__":
    app.run(debug=True)

