from db import count_items, get_connection, upsert_items
from importer import normalize


def make_entry(title, outlet, entry_id="abc"):
    return {
        "title": title,
        "source": {"title": outlet},
        "id": entry_id,
        "link": "https://example.com",
        "published": "Mon, 19 Oct 2026 20:29:00 GMT",
    }


def test_splits_title_and_outlet():
    item = normalize(make_entry("Câmara aprova obras no Passeio Alegre - A Voz da Póvoa", "A Voz da Póvoa"))
    assert item["title"] == "Câmara aprova obras no Passeio Alegre"
    assert item["outlet"] == "A Voz da Póvoa"
    assert item["status"] == "ok"


def test_keeps_hyphens_inside_the_title():
    item = normalize(make_entry("Póvoa - Vila do Conde: nova ciclovia aprovada - Jornal", "Jornal"))
    assert item["title"] == "Póvoa - Vila do Conde: nova ciclovia aprovada"


def test_title_with_only_outlet_name_needs_review():
    item = normalize(make_entry("MAIS - maissemanario", "maissemanario"))
    assert item["status"] == "needs_review"


def test_upsert_twice_does_not_duplicate():
    conn = get_connection(":memory:")
    items = [normalize(make_entry("Título com várias palavras - Jornal", "Jornal", "id-1"))]
    upsert_items(conn, items)
    upsert_items(conn, items)
    assert count_items(conn) == 1


def test_upsert_keeps_reviewed_status():
    conn = get_connection(":memory:")
    items = [normalize(make_entry("Título com várias palavras - Jornal", "Jornal", "id-1"))]
    upsert_items(conn, items)
    conn.execute("UPDATE items SET status = 'rejected'")
    upsert_items(conn, items)
    assert conn.execute("SELECT status FROM items").fetchone()[0] == "rejected"
