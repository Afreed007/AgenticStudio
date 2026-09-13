"""Deterministic mock LLM provider for offline testing and development."""

from typing import Dict, List, Optional
import json


class MockLLMProvider:
    """Simulates realistic LLM responses for each role in the software agency."""

    def __init__(self):
        self.dev_attempt_count: int = 0

    def generate_prd(self, prompt: str) -> Dict:
        return {
            "project_name": "url_shortener_service",
            "summary": "High-performance URL Shortener REST service with SQLite persistence and analytics.",
            "target_audience": "Developers and marketing teams needing short redirects.",
            "user_stories": [
                {
                    "id": "US-1",
                    "title": "Shorten URL",
                    "acceptance_criteria": [
                        "Accept a long URL and return a unique 6-character short code",
                        "Validate that input is a valid HTTP/HTTPS URL",
                        "Store mapping in SQLite database"
                    ]
                },
                {
                    "id": "US-2",
                    "title": "Redirect & Click Count",
                    "acceptance_criteria": [
                        "Lookup short code and return HTTP 307 redirect",
                        "Increment click counter on redirect",
                        "Return 404 for unknown codes"
                    ]
                }
            ],
            "tech_stack_recommendation": ["Python 3.13", "SQLite3", "FastAPI / HTTP routing"]
        }

    def generate_architecture(self, prd_dict: Dict) -> Dict:
        return {
            "project_name": prd_dict.get("project_name", "app"),
            "tech_stack": {
                "language": "Python 3.13",
                "database": "SQLite3",
                "framework": "Pure Python + Standard Library / Minimal REST"
            },
            "file_tree": [
                "url_shortener/__init__.py",
                "url_shortener/models.py",
                "url_shortener/service.py",
                "tests/__init__.py",
                "tests/test_shortener.py"
            ],
            "api_contracts": {
                "POST /shorten": {"input": {"url": "str"}, "output": {"short_code": "str"}},
                "GET /{code}": {"output": "307 redirect to target URL"},
                "GET /stats/{code}": {"output": {"clicks": "int"}}
            },
            "db_schema": "CREATE TABLE IF NOT EXISTS urls (code TEXT PRIMARY KEY, target_url TEXT, clicks INTEGER DEFAULT 0);",
            "notes": "Modular, clean architecture with separation between storage and service layers."
        }

    def generate_code_for_ticket(self, ticket_id: str, title: str, bug_report: Optional[Dict] = None) -> Dict[str, str]:
        """Simulate developer generating code.

        On the first attempt, it intentionally produces a slight edge-case bug.
        When provided with a bug_report, it generates the fixed code.
        """
        if bug_report:
            # Fix attempt: handle invalid URL validation and empty code
            service_code = '''"""URL Shortener Service implementation with SQLite storage."""

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
'''
            return {
                "url_shortener/__init__.py": 'from .service import URLShortener\n__all__ = ["URLShortener"]\n',
                "url_shortener/service.py": service_code
            }
        else:
            # First attempt: Missing URL regex validation, which test_shortener will catch!
            flawed_service_code = '''"""URL Shortener Service implementation with SQLite storage."""

import sqlite3
import hashlib
from typing import Optional, Dict


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
        # BUG: Missing URL format validation!
        code = hashlib.md5(url.encode("utf-8")).hexdigest()[:6]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO urls (code, target_url, clicks) VALUES (?, ?, 0)",
                (code, url)
            )
            conn.commit()
        return code

    def resolve(self, code: str) -> Optional[str]:
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
'''
            return {
                "url_shortener/__init__.py": 'from .service import URLShortener\n__all__ = ["URLShortener"]\n',
                "url_shortener/service.py": flawed_service_code
            }

    def generate_qa_tests(self, ticket_title: str) -> str:
        return '''"""Automated QA Test Suite for URL Shortener."""

import pytest
from url_shortener.service import URLShortener


@pytest.fixture
def shortener(tmp_path):
    db_file = str(tmp_path / "test.db")
    return URLShortener(db_path=db_file)


def test_shorten_valid_url(shortener):
    code = shortener.shorten("https://example.com/long/path")
    assert len(code) == 6
    resolved = shortener.resolve(code)
    assert resolved == "https://example.com/long/path"


def test_invalid_url_raises_error(shortener):
    with pytest.raises(ValueError, match="Invalid URL"):
        shortener.shorten("not-a-valid-url")


def test_click_tracking(shortener):
    code = shortener.shorten("https://google.com")
    stats_before = shortener.get_stats(code)
    assert stats_before["clicks"] == 0

    shortener.resolve(code)
    shortener.resolve(code)

    stats_after = shortener.get_stats(code)
    assert stats_after["clicks"] == 2


def test_unknown_code_returns_none(shortener):
    assert shortener.resolve("nonexistent") is None
'''

    def generate_devops_bundle(self, project_name: str) -> Dict[str, str]:
        dockerfile = """FROM python:3.13-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir pytest
CMD ["pytest", "tests/"]
"""
        readme = f"""# {project_name.replace('_', ' ').title()}

Autonomous production-ready build generated by **Agentic Studio**.

## Architecture
- **Language**: Python 3.13
- **Storage**: SQLite3
- **Tests**: Pytest suite with 100% pass rate verified by QA Engineer Agent

## Quick Start
```bash
# Run automated tests
pytest tests/
```
"""
        return {
            "Dockerfile": dockerfile,
            "README.md": readme
        }
