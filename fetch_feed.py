import feedparser

FEED_URL = "https://news.google.com/rss/search?q=P%C3%B3voa+de+Varzim&hl=pt-PT&gl=PT&ceid=PT:pt-150"

feed = feedparser.parse(FEED_URL)

print(f"Itens no feed: {len(feed.entries)}")

for entry in feed.entries[:10]:
  print("---")
  print("Título:", entry.get("title"))
  print("Jornal:", entry.get("source", {}).get("title"))
  print("Data:", entry.get("published"))
  print("ID:", entry.get("id"))