import feedparser
FEEDS = {
 "Business":"https://feeds.bbci.co.uk/news/business/rss.xml",
 "Technology":"https://feeds.bbci.co.uk/news/technology/rss.xml",
 "Entrepreneurship":"https://www.entrepreneur.com/latest.rss",
 "Finance":"https://feeds.bbci.co.uk/news/business/rss.xml"
}
def get_news(category="Business"):
    feed = feedparser.parse(FEEDS.get(category, FEEDS["Business"]))
    items=[]
    for entry in feed.entries[:12]:
        items.append({
            "title":entry.get("title","Untitled"),
            "source":feed.feed.get("title","RSS source"),
            "published":entry.get("published","Publication date unavailable"),
            "summary":entry.get("summary","")[:500],
            "link":entry.get("link","#")
        })
    return items
