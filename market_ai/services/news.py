
import feedparser
import requests
import re

from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin


# ==========================================
# NEWS SOURCES
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
# CLEAN NEWS TEXT
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
    try:
        cleaner.feed(value)
    except Exception:
        pass

    text = " ".join(cleaner.parts)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================
# FIND IMAGE IN RSS HTML
# ==========================================

class ImageFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.image = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag.lower() == "img" and not self.image:
            self.image = (
                attributes.get("src")
                or attributes.get("data-src")
            )


# ==========================================
# FIND IMAGE IN ARTICLE PAGE
# ==========================================

class MetadataImageFinder(HTMLParser):
    def __init__(self):
        super().__init__()
        self.image = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag.lower() == "meta" and not self.image:
            property_name = (
                attributes.get("property")
                or attributes.get("name")
                or ""
            ).lower()

            if property_name in (
                "og:image",
                "og:image:url",
                "twitter:image",
                "twitter:image:src"
            ):
                self.image = attributes.get("content")

        if tag.lower() == "link" and not self.image:
            rel = attributes.get("rel", "").lower()

            if "image_src" in rel:
                self.image = attributes.get("href")


def valid_image_url(url):
    if not url:
        return None

    url = url.strip()

    if url.startswith("//"):
        url = "https:" + url

    parsed = urlparse(url)

    if parsed.scheme in ("http", "https") and parsed.netloc:
        return url

    return None


def get_article_image(link):
    if not link or link == "#":
        return None

    try:
        response = requests.get(
            link,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
                )
            },
            timeout=(3, 5),
            allow_redirects=True
        )

        if response.status_code != 200:
            return None

        parser = MetadataImageFinder()
        parser.feed(response.text[:300000])

        if parser.image:
            return valid_image_url(
                urljoin(response.url, parser.image)
            )

    except Exception:
        pass

    return None


# ==========================================
# GET IMAGE FROM RSS OR ARTICLE PAGE
# ==========================================

def get_image(entry):

    # RSS media fields
    for field in ["media_content", "media_thumbnail"]:
        media = entry.get(field, [])

        if isinstance(media, dict):
            media = [media]

        for item in media:
            url = valid_image_url(item.get("url"))

            if url:
                return url

    # RSS image enclosures
    for enclosure in entry.get("enclosures", []):
        media_type = enclosure.get("type", "")

        if media_type.startswith("image/"):
            url = valid_image_url(
                enclosure.get("href") or enclosure.get("url")
            )

            if url:
                return url

    # Image embedded in RSS summary
    finder = ImageFinder()

    try:
        finder.feed(entry.get("summary", ""))

        if finder.image:
            url = valid_image_url(finder.image)

            if url:
                return url

    except Exception:
        pass

    # Image embedded in article content
    for content_item in entry.get("content", []):
        finder = ImageFinder()

        try:
            finder.feed(content_item.get("value", ""))

            if finder.image:
                url = valid_image_url(finder.image)

                if url:
                    return url

        except Exception:
            pass

    # Last attempt: inspect publisher article page
    return get_article_image(entry.get("link", ""))


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

            link = entry.get("link", "")

            if not title or not link or link in seen:
                continue

            parsed = urlparse(link)

            if parsed.scheme not in ("http", "https"):
                continue

            seen.add(link)

            summary = clean_text(
                entry.get("summary", "")
            )

            source_info = entry.get("source", {})
            source = source_info.get(
                "title",
                feed.feed.get("title", "News source")
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

            if len(items) >= 8:
                break

        if len(items) >= 8:
            break

    return items
