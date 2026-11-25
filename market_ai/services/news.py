import feedparser
from html.parser import HTMLParser



FEEDS = {
    "Nigeria Business": [
        "https://news.google.com/rss/search?q=Nigeria+business+OR+economy&hl=en-NG&gl=NG&ceid=NG:en"
    ],
    "Nigeria Politics": [
        "https://news.google.com/rss/search?q=Nigeria+politics+OR+government&hl=en-NG&gl=NG&ceid=NG:en"
    ],
    "Nigeria News": [
        "https://news.google.com/rss/search?q=Nigeria+latest+news&hl=en-NG&gl=NG&ceid=NG:en"
    ],
    "Business": [
        "https://feeds.bbci.co.uk/news/business/rss.xml"
    ],
    "Technology & AI": [
        "https://feeds.bbci.co.uk/news/technology/rss.xml"
    ],
    "Entrepreneurship": [
        "https://www.entrepreneur.com/latest.rss"
    ],
    "Finance": [
        "https://news.google.com/rss/search?q=finance+markets&hl=en&gl=US&ceid=US:en"
    ],
    "Africa": [
        "https://feeds.bbci.co.uk/news/world/africa/rss.xml"
    ],
    "International": [
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ]
}


class ImageFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.image = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img" and not self.image:
            attributes = dict(attrs)
            self.image = (
                attributes.get("src")
                or attributes.get("data-src")
            )


def get_image(entry):
    # Images supplied through RSS media fields
    for field in ["media_content", "media_thumbnail"]:
        media = entry.get(field, [])
        if isinstance(media, dict):
            media = [media]

        for item in media:
            url = item.get("url")
            if url:
                return url

    # Images supplied as RSS enclosures
    for enclosure in entry.get("enclosures", []):
        url = enclosure.get("href") or enclosure.get("url")
        media_type = enclosure.get("type", "")

        if url and (
            media_type.startswith("image/")
            or any(url.lower().split("?")[0].endswith(ext)
                   for ext in [".jpg", ".jpeg", ".png", ".webp"])
        ):
            return url

    # Look for an image in the article summary HTML
    finder = ImageFinder()
    finder.feed(entry.get("summary", ""))

    return finder.image


def get_news(category="Business"):
    urls = FEEDS.get(category, FEEDS["Business"])
    items = []
    seen = set()

    for feed_url in urls:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.get("title", "Untitled")
            link = entry.get("link", "#")

            if link in seen:
                continue

            seen.add(link)

            items.append({
                "title": title,
                "source": feed.feed.get("title", "News source"),
                "published": entry.get(
                    "published",
                    "Publication date unavailable"
                ),
                "summary": entry.get("summary", "")[:500],
                "link": link,
                "image": get_image(entry)
            })

            if len(items) >= 12:
                break

        if len(items) >= 12:
            break

    return items
