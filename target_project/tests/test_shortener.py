"""Automated QA Test Suite for URL Shortener."""

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
