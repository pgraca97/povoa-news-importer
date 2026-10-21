# povoa-news-importer

Imports news about Póvoa de Varzim from the Google News RSS feed into a
local SQLite database.

## What it does

1. Fetches the Google News RSS search for "Póvoa de Varzim" (pt-PT).
2. Normalizes each entry: splits the outlet name off the title, converts
   the date to ISO 8601 and flags suspicious titles for review.
3. Upserts the items into `news.db` (table `items`).

```
$ python importer.py
100 lidos, 100 na base de dados
```

## How to run

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python importer.py   # fetch the feed and update news.db
pytest -v            # run the tests
```

Query the results:

```sh
sqlite3 news.db "SELECT published_at, outlet, title FROM items ORDER BY published_at DESC LIMIT 10"
```

## Decisions

- **Deduplication by `(source, external_id)` with upsert.** The pair is
  `UNIQUE`, and re-imports run `INSERT ... ON CONFLICT DO UPDATE`, so the
  importer is idempotent: running it twice gives no duplicates. `source`
  is part of the key so other feeds can be added later without id clashes.
- **`status` is only written on insert.** An item reviewed by hand keeps
  its status when the feed returns it again; the upsert only refreshes
  title, outlet, link and date.
- **Suspicious items are flagged, not discarded.** Titles with fewer than
  3 words, or that are just the outlet name, get `status = needs_review`.
  Dropping them would silently lose real news; flagging leaves the call
  to a human.
- **Dates stored as ISO 8601.** RSS dates come as RFC 822
  (`Tue, 21 Oct 2026 08:00:00 GMT`), which sort by weekday name when
  stored as text. ISO 8601 (`2026-10-21T08:00:00+00:00`) sorts
  chronologically with a plain `ORDER BY`.
- **`requests` with a timeout instead of letting feedparser download.**
  The request fails after 10 s and raises on HTTP errors, where
  feedparser would silently return an empty feed.

## What I found

- **MAIS Semanário has no usable titles.** 9 of the 10 `needs_review`
  items come from this outlet, all titled just `MAIS`. Its site
  (`maissemanario.pt`) serves `<title>MAIS</title>`, advertises no RSS
  feed, and `/feed/`, `/rss` and `/feed.xml` return 404. Google News
  seems to take the page title as is, so the headline never reaches the
  feed. For now this is the only outlet with the problem.
- **The same outlet appears under different names:** `maissemanario` and
  `maissemanario.pt`.
- **A legitimate short title is also flagged:** `Rui Coelho` (Rádio Onda
  Viva) is a real two-word headline. The 3-word rule trades a few false
  positives for catching the empty ones.
- **The feed returns at most 100 items**, which covered about 2.5 months
  (Aug–Oct 2026) of news from 43 outlets. Older items fall off, so the
  importer has to run regularly to keep a full history.
- **Links point to Google, not to the outlet.** Every `link` is a
  `news.google.com/rss/articles/...` URL. Following its redirects only
  goes through Google's consent page and back to Google News; it never
  reaches the article.
- **All dates come in GMT**, so they are stored in UTC (`+00:00`).

## Next steps

- Run on a schedule (cron) so no items are lost to the 100-item limit.
- Detect the same story covered by several outlets (title similarity)
  and group them.
- Recover the real article URL behind the Google News link.
- Normalize outlet names (`maissemanario` / `maissemanario.pt`).
- Suggest tags with an LLM, chosen from a closed list.
- Show dates in `Europe/Lisbon` time; storage stays in UTC.
- Add `first_seen_at` / `last_seen_at` columns to track when items appear
  and drop off the feed.
- Build a small frontend to browse items and work through the
  `needs_review` queue.
