
import os
import requests

BEARER_TOKEN = os.getenv("AAAAAAAAAAAAAAAAAAAAAB4i5AEAAAAAKrOouPFkj4RqB9t4oUlM23RXDVo%3DRuNCOXrvkwSjm9xStodMFEvAnq5IypMkZc1zZOubdFANuh7tWI")

def get_trending_posts(limit=4):
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}

    # Using X API v2 “tweets/search/recent” endpoint
    query = "lang:en -is:retweet"
    url = f"https://api.x.com/2/tweets/search/recent?query={query}&tweet.fields=public_metrics,author_id&max_results=50"

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching tweets: {resp.text}")
        return []

    tweets = resp.json().get("data", [])
    scored = []

    for t in tweets:
        metrics = t.get("public_metrics", {})
        likes = metrics.get("like_count", 0)
        reposts = metrics.get("retweet_count", 0)
        replies = metrics.get("reply_count", 0)
        score = (likes * 0.5) + (reposts * 0.3) + (replies * 0.2)
        scored.append({
            "id": t["id"],
            "author": t["author_id"],
            "text": t["text"],
            "score": score
        })

    # Sort & return top 4
    top = sorted(scored, key=lambda x: x["score"], reverse=True)[:limit]
    return top
