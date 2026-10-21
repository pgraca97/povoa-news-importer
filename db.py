import sqlite3

DB_PATH = "news.db"


def get_connection(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            source TEXT NOT NULL,
            external_id TEXT NOT NULL,
            outlet TEXT,
            title TEXT,
            link TEXT,
            published_at TEXT,
            status TEXT NOT NULL,
            UNIQUE (source, external_id)
        )
    """)
    return conn


def upsert_items(conn, items):
    # status só entra no INSERT: num item que já existe pode ter sido revisto
    # à mão, e o import seguinte não deve desfazer essa revisão.
    with conn:
        conn.executemany("""
            INSERT INTO items (source, external_id, outlet, title, link, published_at, status)
            VALUES (:source, :external_id, :outlet, :title, :link, :published_at, :status)
            ON CONFLICT (source, external_id) DO UPDATE SET
                outlet = excluded.outlet,
                title = excluded.title,
                link = excluded.link,
                published_at = excluded.published_at
        """, items)


def count_items(conn):
    return conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
