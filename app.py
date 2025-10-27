import os
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from dotenv import load_dotenv

# --- Load environment ---
load_dotenv()
X_BEARER_TOKEN = os.getenv("AAAAAAAAAAAAAAAAAAAAAB4i5AEAAAAAKrOouPFkj4RqB9t4oUlM23RXDVo%3DRuNCOXrvkwSjm9xStodMFEvAnq5IypMkZc1zZOubdFANuh7tWI")
DISCORD_WEBHOOK = os.getenv("https://discord.com/api/webhooks/1431913027044900936/B8P9MbvWOX38aQZKGqLi23RgDynLBEROC0_BTlEKCkB_zgTXBuK8pJrrM7G0jtu_L_gf")

HEADERS = {"Authorization": f"Bearer {X_BEARER_TOKEN}"} if X_BEARER_TOKEN else {}

# --- Flask app ---
app = Flask(__name__)

# --- Fetch top X news posts ---
def fetch_x_chatter(ticker, minutes=2880, max_posts=4):  # 48h
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=minutes)

    url = "https://api.twitter.com/2/tweets/search/recent"
    query = f"${ticker} OR #{ticker} -is:retweet lang:en"
    params = {
        "query": query,
        "max_results": 50,
        "tweet.fields": "text,public_metrics,created_at",
        "start_time": start_time.isoformat("T") + "Z",
        "end_time": end_time.isoformat("T") + "Z"
    }

    r = requests.get(url, headers=HEADERS, params=params)
    if r.status_code != 200:
        print(f"X API Error: {r.status_code}, {r.text}")
        return []

    data = r.json().get("data", [])
    # Sort by engagement and pick top N
    top_posts = sorted(data, key=lambda t: sum(t["public_metrics"].values()), reverse=True)[:max_posts]
    return top_posts

# --- Sentiment analysis ---
def analyze_sentiment(tweets):
    bullish_words = ["buy", "long", "moon", "up", "bull", "call", "pump"]
    bearish_words = ["sell", "short", "down", "dump", "bear", "crash", "put"]

    score = 0
    for t in tweets:
        text = t["text"].lower()
        for w in bullish_words:
            if w in text: score += 1
        for w in bearish_words:
            if w in text: score -= 1
    if tweets:
        score = score / len(tweets)
    return max(-1, min(1, score))

# --- Send Discord notification ---
def send_discord_notification(ticker, signal, sentiment, enriched):
    if not DISCORD_WEBHOOK:
        return
    payload = {
        "content": f"**{ticker}** | TV Signal: {signal.upper()} | X Sentiment: {sentiment:.2f} | Enriched: {enriched}"
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
    except Exception as e:
        print(f"Discord webhook error: {e}")

# --- Webhook endpoint ---
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    ticker = data.get("ticker")
    signal = data.get("signal")  # "bull" or "bear"

    if not ticker or not signal:
        return jsonify({"error": "Missing ticker or signal"}), 400

    # Step 1: Fetch X chatter
    tweets = fetch_x_chatter(ticker)
    sentiment = analyze_sentiment(tweets)

    # Step 2: Enrich signal
    if signal == "bull" and sentiment >= 0:
        enriched = "STRONG BULL"
    elif signal == "bear" and sentiment <= 0:
        enriched = "STRONG BEAR"
    else:
        enriched = "WEAK SIGNAL"

    # Step 3: Send to Discord
    send_discord_notification(ticker, signal, sentiment, enriched)

    # Return JSON for logging/debug
    return jsonify({
        "ticker": ticker,
        "signal": signal,
        "sentiment": sentiment,
        "enriched": enriched
    })

# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

