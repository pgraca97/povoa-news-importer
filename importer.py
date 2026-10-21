import feedparser
import requests

FEED_URL = "https://news.google.com/rss/search?q=P%C3%B3voa+de+Varzim&hl=pt-PT&gl=PT&ceid=PT:pt-150"
SOURCE = "google_news"


def fetch_entries(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return feedparser.parse(resp.content).entries


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
        "published_at": entry.get("published"),
        "status": "needs_review" if needs_review else "ok",
    }


if __name__ == "__main__":
    items = [normalize(e) for e in fetch_entries(FEED_URL)]
    for item in items[:15]:
        print(item["status"], "|", item["outlet"], "|", item["title"])
    review = sum(1 for i in items if i["status"] == "needs_review")
    print(f"{len(items)} itens, {review} para revisão")
