from email.utils import parsedate_to_datetime

import feedparser
import requests

from db import count_items, get_connection, upsert_items

FEED_URL = "https://news.google.com/rss/search?q=P%C3%B3voa+de+Varzim&hl=pt-PT&gl=PT&ceid=PT:pt-150"
SOURCE = "google_news"


def fetch_entries(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return feedparser.parse(resp.content).entries


def to_iso(rfc822_date):
    # RSS traz "Tue, 21 Oct 2026 08:00:00 GMT"; em ISO 8601 o ORDER BY
    # sobre TEXT fica cronológico.
    if not rfc822_date:
        return None
    return parsedate_to_datetime(rfc822_date).isoformat()


def normalize(entry):
    raw_title = entry.get("title", "")
    outlet = entry.get("source", {}).get("title", "")

    title, sep, _ = raw_title.rpartition(" - ")
    if not sep:
        title = raw_title
    title = title.strip()

    too_short = len(title.split()) < 3
    is_outlet_name = title.lower() in outlet.lower()
    needs_review = too_short or is_outlet_name

    return {
        "source": SOURCE,
        "external_id": entry.get("id"),
        "outlet": outlet,
        "title": title,
        "link": entry.get("link"),
        "published_at": to_iso(entry.get("published")),
        "status": "needs_review" if needs_review else "ok",
    }


if __name__ == "__main__":
    items = [normalize(e) for e in fetch_entries(FEED_URL)]
    conn = get_connection()
    upsert_items(conn, items)
    print(f"{len(items)} lidos, {count_items(conn)} na base de dados")