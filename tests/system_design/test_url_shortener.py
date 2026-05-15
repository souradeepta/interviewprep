import pytest
from python.system_design.url_shortener import URLShortener


class TestURLShortener:
    def test_shorten_and_expand(self):
        shortener = URLShortener()
        long_url = "https://example.com/very/long/path"
        short_code = shortener.shorten(long_url)
        assert shortener.expand(short_code) == long_url

    def test_unique_short_codes(self):
        shortener = URLShortener()
        urls = [
            "https://example.com/url1",
            "https://example.com/url2",
            "https://example.com/url3",
        ]
        short_codes = set()
        for url in urls:
            code = shortener.shorten(url)
            short_codes.add(code)
        assert len(short_codes) == 3

    def test_deduplication(self):
        shortener = URLShortener()
        url = "https://example.com/url"
        code1 = shortener.shorten(url)
        code2 = shortener.shorten(url)
        assert code1 == code2

    def test_expand_nonexistent(self):
        shortener = URLShortener()
        assert shortener.expand("xyz123") is None

    def test_base62_encoding(self):
        shortener = URLShortener()
        code1 = shortener.shorten("https://example.com/1")
        code2 = shortener.shorten("https://example.com/2")
        # Codes should be short
        assert len(code1) < 10
        assert len(code2) < 10
        # Codes should be different
        assert code1 != code2
