"""URL Shortener - Base62 encoding with atomic counter"""

import hashlib


class URLShortener:
    """URL Shortener using atomic counter and Base62 encoding"""

    BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

        """__init__ implementation.

        Time: O(n)
        Space: O(1)
        """
    def __init__(self):
        self.counter = 0
        self.url_map = {}  # short_code -> long_url
        self.reverse_map = {}  # long_url -> short_code (optional)

    def shorten(self, long_url: str) -> str:
        """Convert long URL to short code"""
        # Check if already shortened
        if long_url in self.reverse_map:
            return self.reverse_map[long_url]

        # Encode counter to Base62
        self.counter += 1
        short_code = self._encode(self.counter)

        self.url_map[short_code] = long_url
        self.reverse_map[long_url] = short_code
        return short_code

    def expand(self, short_code: str) -> str:
        """Convert short code back to long URL"""
        return self.url_map.get(short_code, None)

    def _encode(self, num: int) -> str:
        """Encode number to Base62"""
        if num == 0:
            return self.BASE62_CHARS[0]

        chars = []
        while num > 0:
            chars.append(self.BASE62_CHARS[num % 62])
            num //= 62

        return ''.join(reversed(chars))

    def _decode(self, code: str) -> int:
        """Decode Base62 to number"""
        num = 0
        for char in code:
            num = num * 62 + self.BASE62_CHARS.index(char)
        return num


if __name__ == "__main__":
    shortener = URLShortener()

    urls = [
        "https://www.example.com/very/long/url/path",
        "https://github.com/user/repo",
        "https://stackoverflow.com/questions/1234567/how-to-code",
    ]

    for url in urls:
        short = shortener.shorten(url)
        print(f"{url[:40]}... -> {short}")
        print(f"  Expand: {shortener.expand(short)[:40]}...")