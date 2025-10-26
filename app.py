from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# -------------------------
# Root route for testing
# -------------------------
@app.route("/")
def home():
    return jsonify({"message": "X News App is running!"})

# -------------------------
# Webhook route for TradingView alerts
# -------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    ticker = data.get("ticker")
    signal = data.get("signal")
    if not ticker or not signal:
        return jsonify({"error": "Missing ticker or signal"}), 400

    # Fetch top 4 trending X posts (dummy example)
    top_posts = fetch_x_posts(ticker, limit=4)

    # Optionally send Discord notification
    discord_webhook = os.environ.get("DISCORD_WEBHOOK")
    if discord_webhook:
        send_discord_notification(discord_webhook, ticker, signal, top_posts)

    return jsonify({"status": "success", "ticker": ticker, "signal": signal, "top_posts": top_posts})

# -------------------------
# Fetch top X posts (dummy example)
# -------------------------
def fetch_x_posts(ticker, limit=4):
    # Replace with actual X API call if available
    # Here we just simulate trending posts
    posts = [
        {"user": "UserA", "text": f"{ticker} is bullish! 🚀"},
        {"user": "UserB", "text": f"{ticker} is breaking out!"},
        {"user": "UserC", "text": f"{ticker} news update."},
        {"user": "UserD", "text": f"{ticker} watch closely."},
    ]
    return posts[:limit]

# -------------------------
# Send Discord notification
# -------------------------
def send_discord_notification(webhook_url, ticker, signal, posts):
    content = f"TradingView Alert: {ticker} → {signal}\nTop {len(posts)} X posts:\n"
    for p in posts:
        content += f"- {p['user']}: {p['text']}\n"
    payload = {"content": content}
    try:
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print("Failed to send Discord notification:", e)

# -------------------------
# Run the app
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

