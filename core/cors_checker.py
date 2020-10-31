import asyncio
import aiohttp
import tldextract
import sys
import math
import inspect

from core.register import Register
from common.logger import get_logger

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from urllib.parse import urlparse
except ImportError:
    logging.warning("Importing urllib.parse failed. Importing urlparse now.")
    from urlparse import urlparse


class CORSChecker:

    headers = None
    register = Register()

    def __init__(self, urls, sem_size, stats, headers=None, char_mode=0, is_proxy=False, if_report=False):
        self.urls = urls
        self.char_mode = char_mode
        self.stats = stats
        self.is_proxy = is_proxy
        self.if_report = if_report

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.semaphore = asyncio.Semaphore(sem_size)

        if headers is not None:
            self.headers = headers
        
        if self.is_proxy:
            self.proxy = 'http://127.0.0.1:8080'
        else:
            self.proxy = None

        self.logger = get_logger()

    async def fetch(self, url, headers, resp_data):
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.head(
                url,
                ssl=False,
                timeout=10,
                allow_redirects=True,
                proxy=self.proxy
            ) as resp:
                resp_data['headers'] = resp.headers
                resp_data['status'] = resp.status
                resp_data['url'] = resp.url

                self.logger.debug(str(resp.status) + ":: URL: " + url + " :: Testing: " + headers['Origin'])
                return await resp.read()

    async def bound_fetch(self, url, headers, resp_data):
        async with self.semaphore:
            await self.fetch(url, headers, resp_data)

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
        except TimeoutError as err:
            self.log_exception(url, test_origin)
            self.logger.error(err, exc_info=True)
            return None
        except:
            self.log_exception(url, test_origin)
            return None

        # Statistics & flow control
        if not self.valid_status_code(url, test_origin, resp_data):
            return None
        if not self.valid_redirection_status(url, test_origin, resp_data):
            return None

        self.log_stats('worked', url)
        return resp_data

    def log_exception(self, url, test_origin):
        self.log_stats('excepted', url)
        self.logger.warning("Exception during fetching for URL:" + url + " and origin: " + test_origin)

    def valid_status_code(self, url, test_origin, resp_data):
        if math.floor(resp_data['status'] / 100) == 4:
            self.log_stats('status_400', url)
            self.logger.debug("Returned status code 400 for URL:" + url + " and origin: " + test_origin)
            return False
        return True

    def valid_redirection_status(self, url, test_origin, resp_data):
        if not self.validate_domain_redirection(url, resp_data['url']):
            self.log_stats('redirected', url)
            self.logger.debug("Redirected to another domain for URL:" + url + " and origin: " + test_origin + " redirected to the: " + str(resp_data['url']))
            return False
        return True

    def validate_domain_redirection(self, url, resp_url):
        domain = tldextract.extract(url).registered_domain
        resp_domain = tldextract.extract(str(resp_url)).registered_domain
        if domain.lower() != resp_domain.lower():
            return False
        return True

    def log_stats(self, type, log):
        self.stats.data[type].append(log)

    async def check_cors_policy(self, fname, url, test_origin):
        resp_data = await self.send_request(url, test_origin)

        if resp_data is not None:
            resp_origin = resp_data['headers'].get('access-control-allow-origin')
            resp_credentials = resp_data['headers'].get('access-control-allow-credentials')

            if test_origin == resp_origin:
                self.logger.info("Returned the same origin for: " + url + " when testing for origin: " + test_origin)
                self.add_vuln_domain('mirrored_origin', fname, url, test_origin)
            if resp_credentials == "true":
                self.logger.info("Returned with credentials for: " + url + " when testing for origin: " + test_origin)
                self.add_vuln_domain('credentials', fname, url, test_origin)

    def add_vuln_domain(self, type, fname, url, test_origin):
        log = {
            'fname': fname,
            'url': url,
            'test_origin': test_origin
        }
        if type == 'mirrored_origin':
            self.log_stats('mirrored_vuln', log)
        elif type == 'credentials':
            self.log_stats('credentials_vuln', log)

    # "https://evil.com"
    @register
    async def test_reflect_origin(self, url):
        fname = inspect.stack()[0][3]
        parsed_url = urlparse(url)
        test_origin = parsed_url.scheme + "://" + "evil.com"
        await self.check_cors_policy(fname, url, test_origin)

    # "https://www.example.evil.com"
    @register
    async def test_prefix_match(self, url):
        fname = inspect.stack()[0][3]
        parsed_url = urlparse(url)
        test_origin = parsed_url.scheme + "://" + parsed_url.netloc.split(':')[0] + ".evil.com"
        await self.check_cors_policy(fname, url, test_origin)

    # "https://evilexample.com"
    @register
    async def test_suffix_match(self, url):
        fname = inspect.stack()[0][3]
        parsed_url = urlparse(url)
        sld = tldextract.extract(url.strip()).registered_domain
        test_origin = parsed_url.scheme + "://" + "evil" + sld
        await self.check_cors_policy(fname, url, test_origin)

    # "null"
    @register
    async def test_null(self, url):
        fname = inspect.stack()[0][3]
        test_origin = "null"
        await self.check_cors_policy(fname, url, test_origin)

    # "https://evil.www.example.com"
    @register
    async def test_any_subdomain(self, url):
        fname = inspect.stack()[0][3]
        parsed_url = urlparse(url)
        test_origin = parsed_url.scheme + "://" + "evil." + parsed_url.netloc.split(':')[0]
        await self.check_cors_policy(fname, url, test_origin)

    # "http://example.com" (for https)
    @register
    async def test_http_trust(self, url):
        fname = inspect.stack()[0][3]
        parsed_url = urlparse(url)
        if parsed_url.scheme != "https":
            return

        test_origin = "http://" + parsed_url.netloc.split(':')[0]
        await self.check_cors_policy(fname, url, test_origin)

    # "http://example_.com"
    @register
    async def test_special_characters(self, url):
        fname = inspect.stack()[0][3]
        parsed_url = urlparse(url)
        if self.char_mode == 0:
            special_characters = ['_', '%60', '-', '{', '`']
        elif self.char_mode == 1:
            special_characters = ['_', '-', '"', '+', '%60', '`', ';', '|', '&', "'", ',', '$', '=', "%0b"]
        elif self.char_mode == 2:
            special_characters = ['_','-','"','{','}','+','^','%60','!','~','`',';','|','&',"'",'(',')','*',',','$','=','+',"%0b"]
        origins = []

        for char in special_characters:
            attempt = parsed_url.scheme + "://" + parsed_url.netloc.split(':')[0] + char + ".evil.com"
            origins.append(attempt)

        for test_origin in origins:
            await self.check_cors_policy(fname, url, test_origin)

    # "http://wwwAexample.com"
    @register
    async def test_dot_to_char(self, url):
        fname = inspect.stack()[0][3]
        parsed_url = urlparse(url)
        split_url = parsed_url.netloc.split('.')
        if len(split_url) > 2:
            test_origin = parsed_url.scheme + "://" + 'A'.join(split_url[:-1]) + '.' + split_url[-1]
        else:
            test_origin = parsed_url.scheme + "://" + 'evilA' + '.'.join(split_url)
        await self.check_cors_policy(fname, url, test_origin)

    def run(self):
        tasks = []
        # Default policy for Python 3.8 cannot handle proxy, which could be useful for debugging
        if sys.platform == 'win32' and self.is_proxy:
            loop_policy = asyncio.WindowsSelectorEventLoopPolicy()
            asyncio.set_event_loop_policy(loop_policy)

        loop = asyncio.get_event_loop()

        for url in self.urls:
            for func in self.register:
                tasks.append(asyncio.ensure_future(func(self, url)))
        loop.run_until_complete(asyncio.gather(*tasks))

        self.stats.print_results()
        if self.if_report:
            self.stats.save_json()
