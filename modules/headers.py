# wordpress_bruteforce/modules/headers.py
from fake_useragent import UserAgent
from urllib.parse import urlparse
import random


class HeaderManager:
    """Advanced header management with 1500+ real user agents"""

    def __init__(self, target_url):
        self.target_url = target_url
        self.ua = UserAgent()
        self.referers = self._generate_referers()

    def _generate_referers(self):
        """Generate realistic referer chain"""
        parsed = urlparse(self.target_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        return [
            base,
            f"{base}/wp-admin",
            f"{base}/wp-login.php",
            "https://www.google.com/",
            "https://www.facebook.com/",
            "https://twitter.com/",
        ]

    def generate(self):
        """Generate headers with advanced randomization"""
        base_headers = {
            "User-Agent": self.ua.random,
            "Accept": random.choice([
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "application/json, text/javascript, */*; q=0.01"
            ]),
            "Accept-Encoding": random.choice([
                "gzip, deflate, br",
                "identity;q=1, *;q=0"
            ]),
            "Accept-Language": random.choice([
                "en-US,en;q=0.9",
                "fr-FR,fr;q=0.8,en-US;q=0.7",
                "de-DE,de;q=0.7,en;q=0.3"
            ]),
            "Cache-Control": random.choice([
                "max-age=0",
                "no-cache",
                "no-store"
            ]),
            "Sec-CH-UA": f'"Not.A/Brand";v="8", "Chromium";v="{random.randint(100, 121)}"',
            "Sec-CH-UA-Mobile": random.choice(["?0", "?1"]),
            "Sec-CH-UA-Platform": random.choice(['"Windows"', '"Linux"', '"macOS"'])
        }

        # 30% chance to add extra headers
        if random.random() < 0.3:
            base_headers.update({
                "X-Requested-With": random.choice(["XMLHttpRequest", "com.wordpress.app"]),
                "X-WP-Nonce": "".join(random.choices("abcdef0123456789", k=32)),
                "X-Forwarded-Proto": random.choice(["https", "http"]),
                "TE": random.choice(["trailers", "compress"])
            })

        return base_headers
