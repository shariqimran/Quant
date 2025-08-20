# requirements: feedparser, vaderSentiment, beautifulsoup4, html5lib, numpy
import feedparser, numpy as np, re, time
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

an = SentimentIntensityAnalyzer()

def strip_html(s):
    return BeautifulSoup(s or "", "html5lib").get_text(" ", strip=True)

def fetch_reddit_rss(symbol, subs=("stocks","investing","wallstreetbets","CryptoCurrency"), limit_per=30):
    items=[]
    for sr in subs:
        url=f"https://www.reddit.com/r/{sr}/search.rss?q=%24{symbol}&sort=new&restrict_sr=on"
        feed=feedparser.parse(url)
        for e in feed.entries[:limit_per]:
            txt = strip_html(e.get("title","")) + " " + strip_html(e.get("summary",""))
            items.append({"platform":"reddit","text":txt[:500], "link":e.get("link"), "ts":e.get("published","")})
        time.sleep(0.6)  # be polite; avoid rate hits
    return items

def fetch_google_news(symbol, limit=50):
    url=f"https://news.google.com/rss/search?q={symbol}&hl=en-CA&gl=CA&ceid=CA:en"
    feed=feedparser.parse(url)
    items=[]
    for e in feed.entries[:limit]:
        txt = strip_html(e.get("title","")) + " " + strip_html(e.get("summary",""))
        items.append({"platform":"news","text":txt[:500], "link":e.get("link"), "ts":e.get("published","")})
    return items

def score_items(items):
    scored=[]
    for it in items:
        t = re.sub(r"\s+"," ", it["text"]).strip()
        if len(t)<10: 
            continue
        s = an.polarity_scores(t)["compound"]  # [-1,1]
        it["sentiment"]=s
        scored.append(it)
    return scored

def decide(scored):
    if not scored: 
        return {"verdict":"Neutral","confidence":0.2,"metrics":{},"reasons":[]}
    scores=np.array([x["sentiment"] for x in scored])
    S=float(np.mean(scores))
    breadth=float((scores>0).mean() - (scores<0).mean())
    intensity=float(np.mean(np.abs(scores)))
    V=len(scored)  # for MVP, treat as raw volume

    if S<-0.2 and V>40:    verdict, conf = "Avoid", min(1.0, 0.5+abs(S))
    elif S>+0.2 and V>20:  verdict, conf = "Favorable", min(1.0, 0.5+S)
    else:                  verdict, conf = "Neutral", 0.5

    top = sorted(scored, key=lambda r: abs(r["sentiment"]), reverse=True)[:3]
    reasons=[{"excerpt":r["text"][:180], "score":r["sentiment"], "link":r["link"], "src":r["platform"]} for r in top]
    return {"verdict":verdict, "confidence":conf, "metrics":{"S":S,"V":V,"breadth":breadth,"intensity":intensity}, "reasons":reasons}

def analyze_symbol(symbol):
    posts = fetch_reddit_rss(symbol) + fetch_google_news(symbol)
    scored = score_items(posts)
    return decide(scored)

# demo
# print(analyze_symbol("NVDA"))
