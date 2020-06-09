import asyncio
import aiohttp
import tldextract
import sys

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CORSChecker():

    headers = None
    functions = [
        'test_reflect_origin',
        'test_prefix_match',
        'test_suffix_match',
        'test_null',
        'test_any_subdomain',
        'test_http_trust'
    ]

    def __init__(self, urls, sem_size, headers=None):
        self.urls = urls
        self.semaphore = asyncio.Semaphore(sem_size)

        # for debugging
        self.excepted = [0]
        self.nulled = [0]
        self.redirected = [0]
        self.four = [0]
        self.good = [0]

        if headers is not None:
            self.headers = headers

        # Default policy for Python 3.8 cannot handle proxy, which could be useful for debugging
        if sys.platform == 'win32':
            self.loop_policy = asyncio.WindowsSelectorEventLoopPolicy()

        # Only if CorsChecker is going to extend multiprocessing.Process, if not throw it away to the begging of file/main
        try:
            import uvloop
            uvloop.install()
        except ImportError:
            pass


    async def fetch(self, url, headers, resp_data):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                url,
                ssl=False,
                timeout=30,
                allow_redirects=True,
                # proxy='http://127.0.0.1:8081',
            ) as resp:
                # Check later if it is possible to return data in more elegant way
                resp_data['headers'] = resp.headers
                resp_data['status'] = resp.status
                resp_data['url'] = resp.url
                # debug print
                print(str(resp.status) + " : " + url)
                return await resp.read()


    async def bound_fetch(self, url, headers, resp_data):
        async with self.semaphore:
            await self.fetch(url, headers, resp_data)


    def validate_domain_redirection(self, url, resp_url):
        domain = tldextract.extract(url).registered_domain
        resp_domain = tldextract.extract(str(resp_url)).registered_domain

        if domain.lower() != resp_domain.lower():
            return False
        return True


    async def send_request(self, url, test_origin):
        # Add some user-agent randomizer later
        headers = {
            'Origin' : test_origin,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
        }

        if self.headers is not None:
            headers.update(self.headers)

        resp_data = dict()
        try:
            resp_data['response'] = await self.bound_fetch(url, headers, resp_data)
        except:
            self.excepted[0] = self.excepted[0] + 1
            self.excepted.append(url)
            print("Except : " + url)
            return None
        # Lot of debug saves/prints
        if resp_data is None:
            self.nulled[0] = self.excepted[0] + 1
            self.nulled.append(url)
            print("None Except : " + url)
            return None

        if resp_data['status'] == 400:
            self.four[0] = self.four[0] + 1
            self.four.append(url)
            print("400 Except : " + url)
            return None

        if not self.validate_domain_redirection(url, resp_data['url']):
            self.redirected[0] = self.redirected[0] + 1
            self.redirected.append(url)
            print("Redirect Except : " + url)
            return None

        self.good[0] = self.good[0] + 1
        self.good.append(url)
        return resp_data


    async def check_cors_policy(self, url, test_origin):
        resp_data = await self.send_request(url, test_origin)

        if resp_data is not None:
            resp_origin = resp_data['headers'].get('access-control-allow-origin')
            resp_credentials = resp_data['headers'].get('access-control-allow-credentials')

            if test_origin == resp_origin:
                print("The same origin returned for: " + str(url) + " : " + str(resp_origin) + " | " + str(test_origin))
            if resp_credentials == "true":
                print("With credentials! " + str(url) + " : " + str(resp_origin) + " | " + str(test_origin))

    # "https://evil.com"
    async def test_reflect_origin(self, url):
        parsed_url = urlparse(url)
        test_origin = parsed_url.scheme + "://" + "evil.com"
        await self.check_cors_policy(url, test_origin)

    # "https://www.example.evil.com"
    async def test_prefix_match(self, url):
        parsed_url = urlparse(url)
        test_origin = parsed_url.scheme + "://" + parsed_url.netloc.split(':')[0] + ".evil.com"
        await self.check_cors_policy(url, test_origin)

    # "https://evilexample.com"
    async def test_suffix_match(self, url):
        parsed_url = urlparse(url)
        sld = tldextract.extract(url.strip()).registered_domain
        test_origin = parsed_url.scheme + "://" + "evil" + sld
        await self.check_cors_policy(url, test_origin)

    # "null"
    async def test_null(self, url):
        test_origin = "null"
        await self.check_cors_policy(url, test_origin)

    # "https://evil.www.example.com"
    async def test_any_subdomain(self, url):
        parsed_url = urlparse(url)
        test_origin = parsed_url.scheme + "://" + "evil." + parsed_url.netloc.split(':')[0]
        await self.check_cors_policy(url, test_origin)

    # "http://example.com" (for https)
    async def test_http_trust(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme != "https":
            return

        test_origin = "http://" + parsed_url.netloc.split(':')[0]
        await self.check_cors_policy(url, test_origin)

    #Todo more methods
    # "https://exampleAevil.com" "https://testAexampleAevil.com"
    # "https://test.exampleAevil.com"
    # "https://example[special_character].evil.com"

    def run(self):
        tasks = []
        asyncio.set_event_loop_policy(self.loop_policy)
        loop = asyncio.get_event_loop()

        for url in self.urls:
            for fname in self.functions:
                func = getattr(self, fname)
                tasks.append(asyncio.ensure_future(func(url)))

        loop.run_until_complete(asyncio.gather(*tasks))

        self.print_results()

    #Debug
    def print_results(self):
        print("--------------------------------------------")
        print("Exception during connection:")
        print(self.excepted)
        print("Empty response:")
        print(self.nulled)
        print("400 returned:")
        print(self.four)
        print("Redirected to another domain:")
        print(self.redirected)
        print("Working examples")
        print(self.good)
        print("--------------------------------------------")

