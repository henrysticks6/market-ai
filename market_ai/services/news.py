
import feedparser
import re
import requests
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse


# ==========================================
# MARKET AI NEWS SOURCES
# ==========================================

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


# ==========================================
# CLEAN HTML FROM NEWS CONTENT
# ==========================================

class TextCleaner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def clean_text(value):
    value = unescape(str(value or ""))

    cleaner = TextCleaner()
    cleaner.feed(value)

    text = " ".join(cleaner.parts)

    # Remove exposed HTML attributes and URLs
    text = re.sub(
        r'href\s*=\s*["\']?.*?["\']?(?=\s|$)',
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r'https?://\S+',
        "",
        text
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


# ==========================================
# EXTRACT PUBLISHER IMAGES
# ==========================================

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

    for field in ["media_content", "media_thumbnail"]:

        media = entry.get(field, [])

        if isinstance(media, dict):
            media = [media]

        for item in media:
            url = item.get("url")

            if url:
                return url

    # Check image enclosures
    for enclosure in entry.get("enclosures", []):

        url = enclosure.get("href") or enclosure.get("url")
        media_type = enclosure.get("type", "")

        if url and (
            media_type.startswith("image/")
            or any(
                url.lower().split("?")[0].endswith(ext)
                for ext in [".jpg", ".jpeg", ".png", ".webp"]
            )
        ):
            return url

    # Check images embedded in summary
    finder = ImageFinder()

    try:
        finder.feed(entry.get("summary", ""))
    except Exception:
        pass

    return finder.image


# ==========================================
# GET NEWS
# ==========================================

def get_news(category="Business"):

    urls = FEEDS.get(category, FEEDS["Business"])

    items = []
    seen = set()

    for feed_url in urls:

        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            continue

        for entry in feed.entries:

            title = clean_text(
                entry.get("title", "News update")
            )

            link = entry.get("link", "#")

            if not title or link in seen:
                continue

            # Keep only valid web article links
            parsed_link = urlparse(link)

            if parsed_link.scheme not in ("http", "https"):
                continue

            seen.add(link)

            summary = clean_text(
                entry.get("summary", "")
            )

            # Prefer publisher name supplied by RSS
            source = feed.feed.get(
                "title",
                "News source"
            )

            published = clean_text(
                entry.get(
                    "published",
                    "Publication date unavailable"
                )
            )

            items.append({
                "title": title,
                "source": clean_text(source),
                "published": published,
                "summary": summary[:500],
                "link": link,
                "image": get_image(entry)
            })

            if len(items) >= 12:
                break

        if len(items) >= 12:
            break

    return items
