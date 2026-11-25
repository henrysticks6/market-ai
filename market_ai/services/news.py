
import feedparser
import requests
import re

from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse


# ==========================================
# MARKET AI NEWS SOURCES
# Direct publisher feeds instead of Google News
# ==========================================

FEEDS = {
    "Nigeria Business": [
        "https://rss.punchng.com/v1/category/business",
        "https://www.premiumtimesng.com/category/business/business-news/feed"
    ],

    "Nigeria Politics": [
        "https://rss.punchng.com/v1/category/politics",
        "https://www.premiumtimesng.com/feed"
    ],

    "Nigeria News": [
        "https://rss.punchng.com/v1/category/latest_news",
        "https://www.premiumtimesng.com/feed"
    ],

    "Business": [
        "https://rss.punchng.com/v1/category/business",
        "https://feeds.bbci.co.uk/news/business/rss.xml"
    ],

    "Technology & AI": [
        "https://rss.punchng.com/v1/category/technology",
        "https://feeds.bbci.co.uk/news/technology/rss.xml"
    ],

    "Entrepreneurship": [
        "https://rss.punchng.com/v1/category/business",
        "https://www.entrepreneur.com/latest.rss"
    ],

    "Finance": [
        "https://www.premiumtimesng.com/category/business/business-news/feed",
        "https://feeds.bbci.co.uk/news/business/rss.xml"
    ],

    "Africa": [
        "https://feeds.bbci.co.uk/news/world/africa/rss.xml"
    ],

    "International": [
        "https://feeds.bbci.co.uk/news/world/rss.xml"
    ]
}


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
    )
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
# FIND IMAGES IN HTML
# ==========================================

class ArticleImageFinder(HTMLParser):

    def __init__(self):
        super().__init__()
        self.image = None

    def handle_starttag(self, tag, attrs):

        attributes = dict(attrs)

        if tag.lower() == "meta" and not self.image:

            name = (
                attributes.get("property")
                or attributes.get("name")
                or ""
            ).lower()

            if name in [
                "og:image",
                "og:image:url",
                "twitter:image",
                "twitter:image:src"
            ]:
                self.image = attributes.get("content")

        if tag.lower() == "img" and not self.image:

            self.image = (
                attributes.get("src")
                or attributes.get("data-src")
            )

            if not self.image:
                srcset = attributes.get("srcset", "")

                if srcset:
                    self.image = srcset.split(",")[0].strip().split(" ")[0]


def valid_image(url, base_url=""):

    if not url:
        return None

    url = url.strip()

    if url.startswith("//"):
        url = "https:" + url

    url = urljoin(base_url, url)

    parsed = urlparse(url)

    if parsed.scheme in ["http", "https"] and parsed.netloc:
        return url

    return None


# ==========================================
# GET IMAGE FROM ARTICLE PAGE
# ==========================================

def get_article_image(link):

    if not link:
        return None

    try:

        response = requests.get(
            link,
            headers=HEADERS,
            timeout=6,
            allow_redirects=True
        )

        if response.status_code != 200:
            return None

        content_type = response.headers.get(
            "Content-Type", ""
        )

        if "text/html" not in content_type.lower():
            return None

        parser = ArticleImageFinder()

        parser.feed(response.text[:400000])

        return valid_image(
            parser.image,
            response.url
        )

    except Exception:
        return None


# ==========================================
# EXTRACT IMAGE FROM RSS ENTRY
# ==========================================

def get_image(entry, feed_url):

    # RSS media content and thumbnails
    for field in ["media_content", "media_thumbnail"]:

        media = entry.get(field, [])

        if isinstance(media, dict):
            media = [media]

        for item in media:

            url = valid_image(
                item.get("url"),
                feed_url
            )

            if url:
                return url

    # RSS image enclosures
    for item in entry.get("enclosures", []):

        media_type = item.get("type", "")

        if media_type.startswith("image/"):

            url = valid_image(
                item.get("href") or item.get("url"),
                feed_url
            )

            if url:
                return url

    # RSS links with image enclosure
    for item in entry.get("links", []):

        if item.get("type", "").startswith("image/"):

            url = valid_image(
                item.get("href"),
                feed_url
            )

            if url:
                return url

    # Images embedded in RSS descriptions
    html_content = entry.get("summary", "")

    for content_item in entry.get("content", []):

        html_content += content_item.get("value", "")

    parser = ArticleImageFinder()

    try:

        parser.feed(html_content)

        if parser.image:

            url = valid_image(
                parser.image,
                feed_url
            )

            if url:
                return url

    except Exception:
        pass

    # Final attempt: publisher's article page
    return get_article_image(
        entry.get("link", "")
    )


# ==========================================
# DOWNLOAD AND PARSE RSS FEEDS
# ==========================================

def get_news(category="Business"):

    urls = FEEDS.get(
        category,
        FEEDS["Business"]
    )

    items = []
    seen = set()

    for feed_url in urls:

        try:

            response = requests.get(
                feed_url,
                headers=HEADERS,
                timeout=12
            )

            response.raise_for_status()

            feed = feedparser.parse(response.content)

        except Exception:
            continue

        if feed.bozo and not feed.entries:
            continue

        for entry in feed.entries:

            title = clean_text(
                entry.get("title", "News update")
            )

            link = entry.get("link", "")

            if not title or not link or link in seen:
                continue

            parsed = urlparse(link)

            if parsed.scheme not in ["http", "https"]:
                continue

            seen.add(link)

            summary = clean_text(
                entry.get("summary", "")
            )

            source_info = entry.get("source", {})

            source = source_info.get(
                "title",
                feed.feed.get("title", "News publisher")
            )

            published = clean_text(
                entry.get(
                    "published",
                    "Publication date unavailable"
                )
            )

            image = get_image(
                entry,
                feed_url
            )

            items.append({
                "title": title,
                "source": clean_text(source),
                "published": published,
                "summary": summary[:500],
                "link": link,
                "image": image
            })

            if len(items) >= 8:
                break

        if len(items) >= 8:
            break

    return items
