"""Experimental sentiment analysis helpers."""

import re
import time

import feedparser
import numpy as np
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


_ANALYZER = SentimentIntensityAnalyzer()


def strip_html(text):
    """Convert HTML-ish text into plain text."""
    return BeautifulSoup(text or "", "html5lib").get_text(" ", strip=True)


def fetch_reddit_rss(symbol, subs=("stocks", "investing", "wallstreetbets", "CryptoCurrency"), limit_per=30):
    """Fetch simple Reddit RSS search results for a symbol."""
    items = []
    for subreddit in subs:
        url = f"https://www.reddit.com/r/{subreddit}/search.rss?q=%24{symbol}&sort=new&restrict_sr=on"
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit_per]:
            text = strip_html(entry.get("title", "")) + " " + strip_html(entry.get("summary", ""))
            items.append(
                {
                    "platform": "reddit",
                    "text": text[:500],
                    "link": entry.get("link"),
                    "ts": entry.get("published", ""),
                }
            )
        time.sleep(0.6)
    return items


def fetch_google_news(symbol, limit=50):
    """Fetch Google News RSS results for a symbol."""
    url = f"https://news.google.com/rss/search?q={symbol}&hl=en-CA&gl=CA&ceid=CA:en"
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:limit]:
        text = strip_html(entry.get("title", "")) + " " + strip_html(entry.get("summary", ""))
        items.append(
            {
                "platform": "news",
                "text": text[:500],
                "link": entry.get("link"),
                "ts": entry.get("published", ""),
            }
        )
    return items


def score_items(items):
    """Attach VADER compound sentiment scores to text items."""
    scored = []
    for item in items:
        text = re.sub(r"\s+", " ", item["text"]).strip()
        if len(text) < 10:
            continue
        item["sentiment"] = _ANALYZER.polarity_scores(text)["compound"]
        scored.append(item)
    return scored


def decide(scored):
    """Convert scored items into a simple sentiment verdict."""
    if not scored:
        return {"verdict": "Neutral", "confidence": 0.2, "metrics": {}, "reasons": []}

    scores = np.array([item["sentiment"] for item in scored])
    sentiment_score = float(np.mean(scores))
    breadth = float((scores > 0).mean() - (scores < 0).mean())
    intensity = float(np.mean(np.abs(scores)))
    volume = len(scored)

    if sentiment_score < -0.2 and volume > 40:
        verdict, confidence = "Avoid", min(1.0, 0.5 + abs(sentiment_score))
    elif sentiment_score > 0.2 and volume > 20:
        verdict, confidence = "Favorable", min(1.0, 0.5 + sentiment_score)
    else:
        verdict, confidence = "Neutral", 0.5

    top_items = sorted(scored, key=lambda item: abs(item["sentiment"]), reverse=True)[:3]
    reasons = [
        {
            "excerpt": item["text"][:180],
            "score": item["sentiment"],
            "link": item["link"],
            "src": item["platform"],
        }
        for item in top_items
    ]

    return {
        "verdict": verdict,
        "confidence": confidence,
        "metrics": {
            "S": sentiment_score,
            "V": volume,
            "breadth": breadth,
            "intensity": intensity,
        },
        "reasons": reasons,
    }


def analyze_symbol(symbol):
    """Fetch and score simple sentiment sources for a symbol."""
    posts = fetch_reddit_rss(symbol) + fetch_google_news(symbol)
    scored = score_items(posts)
    return decide(scored)
