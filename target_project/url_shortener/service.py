"""URL Shortener Service implementation with SQLite storage."""

import sqlite3
import hashlib
import re
from typing import Optional, Dict

URL_REGEX = re.compile(r"^https?://[a-zA-Z0-9.-]+(?:/.*)?$")


class URLShortener:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS urls (
                    code TEXT PRIMARY KEY,
                    target_url TEXT NOT NULL,
                    clicks INTEGER DEFAULT 0
                )"""
            )
            conn.commit()

    def shorten(self, url: str) -> str:
        if not url or not URL_REGEX.match(url):
            raise ValueError(f"Invalid URL: '{url}'")
        code = hashlib.md5(url.encode("utf-8")).hexdigest()[:6]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO urls (code, target_url, clicks) VALUES (?, ?, 0)",
                (code, url)
            )
            conn.commit()
        return code

    def resolve(self, code: str) -> Optional[str]:
        if not code:
            return None
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT target_url, clicks FROM urls WHERE code = ?", (code,))
            row = cur.fetchone()
            if not row:
                return None
            conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,))
            conn.commit()
            return row[0]

    def get_stats(self, code: str) -> Optional[Dict[str, int]]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT clicks FROM urls WHERE code = ?", (code,))
            row = cur.fetchone()
            return {"clicks": row[0]} if row else None
