from __future__ import annotations
import logging
from threading import Lock
from urllib.parse import urldefrag, urljoin, urlparse
import scrapy
from scrapy.http import Response
from technews_crawler.items import CrawledPage

logger = logging.getLogger(__name__)

# Higher priority is scheduled sooner
_PRIORITY_SCALE = 100_000

# Handles comments
def _strip_comment_line(line: str) -> str:
    line = line.strip()
    if not line or line.startswith("#"):
        return ""
    if "#" in line:
        line = line.split("#", 1)[0].strip()
    return line

# Loads URLs from a file
def _load_url_lines(path: str) -> list[str]:
    urls: list[str] = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            u = _strip_comment_line(raw)
            if u:
                urls.append(u)
    return urls

# Loads domain rules from a file
def _load_domain_rules(path: str) -> list[str]:
    rules: list[str] = []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            r = _strip_comment_line(raw)
            if not r:
                continue
            rules.append(r.lower())
    return rules

# Canonicalizes a URL
def _canonicalize_url(url: str) -> str:
    url, _frag = urldefrag(url.strip())
    return url

# Gets the hostname of a URL
def _hostname(url: str) -> str | None:
    try:
        host = urlparse(url).hostname
    except ValueError:
        return None
    return host.lower() if host else None

# Checks if a hostname matches a rule
def _host_matches_rule(hostname: str, rule: str) -> bool:
    hostname = hostname.lower()
    if rule.startswith("."):
        return hostname.endswith(rule)
    return hostname == rule or hostname.endswith("." + rule)

# Checks if a hostname matches any rule
def _host_matches_any_rule(hostname: str, rules: list[str]) -> bool:
    return any(_host_matches_rule(hostname, r) for r in rules)

# Gets the hostnames from seed URLs
def _seed_host_rules(seed_urls: list[str]) -> list[str]:
    hosts: list[str] = []
    for u in seed_urls:
        h = _hostname(u)
        if h:
            hosts.append(h)
    return list(dict.fromkeys(hosts))

class TechnewsSpider(scrapy.Spider):
    name = "tech_news"

    def __init__(
        self,
        seed_file: str | None = None,
        max_pages: str | int = 1000,
        max_depth: str | int = 3,
        allowed_domains_file: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if not seed_file:
            raise ValueError("Spider requires seed file")
        self.seed_file = seed_file
        self.max_pages = int(max_pages)
        self.max_depth = int(max_depth)
        self.allowed_domains_file = allowed_domains_file

        self._page_lock = Lock()
        self._pages_crawled = 0
        self._limit_reached = False

        self._allow_rules: list[str] = []
        self._seeds: list[str] = []

    def start_requests(self):
        self._seeds = [_canonicalize_url(u) for u in _load_url_lines(self.seed_file)]
        if not self._seeds:
            raise ValueError(f"No seed found")

        # Checks if domain is allowed or uses predefined seed hostnames
        if self.allowed_domains_file:
            self._allow_rules = _load_domain_rules(self.allowed_domains_file)
            if not self._allow_rules:
                logger.warning(
                    "%s had no domain rules. Defaulting to seed hostnames",
                    self.allowed_domains_file,
                )
                self._allow_rules = _seed_host_rules(self._seeds)
        else:
            self._allow_rules = _seed_host_rules(self._seeds)

        # Iterates through seeds and checks if they are allowed
        for url in self._seeds:
            if not _hostname(url):
                logger.warning("Skipping invalid seed URL: %s", url)
                continue
            if not self._url_allowed(url):
                logger.warning("Seed URL not allowed: %s", url)
                continue
            yield scrapy.Request(
                url,
                callback=self.parse,
                errback=self._errback,
                meta={"depth": 0},
                priority=self._priority_for_depth(0),
            )

    # Our crawler prioritizes lower depths first using our defined priority scale
    def _priority_for_depth(self, depth: int) -> int:
        return (self.max_depth - depth) * _PRIORITY_SCALE

    def _url_allowed(self, url: str) -> bool:
        host = _hostname(url)
        if not host:
            return False
        if not self._allow_rules:
            return False
        return _host_matches_any_rule(host, self._allow_rules)
    
    def _should_follow_links(self) -> bool:
        with self._page_lock:
            return not self._limit_reached and self._pages_crawled < self.max_pages

    def _should_skip_url(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        return any(path.endswith(f".{ext}") for ext in [
            "pdf", "jpg", "jpeg", "png", "gif", "svg",
            "mp4", "mp3", "zip", "doc", "docx"
        ])

    def parse(self, response: Response):
        depth = int(response.meta.get("depth", 0))

        ctype = (
            response.headers.get(b"Content-Type", b"").decode("latin1", errors="replace")
        )
        is_html = "text/html" in ctype.lower() if ctype else False

        if is_html:
            with self._page_lock:
                if self._pages_crawled >= self.max_pages:
                    return
                self._pages_crawled += 1
                if self._pages_crawled >= self.max_pages:
                    self._limit_reached = True
                    self.crawler.engine.close_spider(self, 'closespider_pagecount')

            yield CrawledPage(
                url=response.url,
                depth=depth,
                status=response.status,
                content_type=ctype,
                body=response.body,
                title=response.css("title::text").get(default=""),
            )

        if not self._should_follow_links():
            return
        if depth >= self.max_depth:
            return
        if not is_html:
            return

        next_depth = depth + 1
        if next_depth > self.max_depth:
            return

        seen_on_page: set[str] = set()
        for href in response.css("a::attr(href)").getall():
            if not href or href.startswith(("#", "mailto:", "javascript:", "tel:")):
                continue
            joined = urljoin(response.url, href.strip())
            joined = _canonicalize_url(joined)
            parsed = urlparse(joined)
            if parsed.scheme not in ("http", "https"):
                continue
            if joined in seen_on_page:
                continue
            seen_on_page.add(joined)

            if self._should_skip_url(joined):
                continue
            if not self._url_allowed(joined):
                continue

            yield scrapy.Request(
                joined,
                callback=self.parse,
                errback=self._errback,
                meta={"depth": next_depth},
                priority=self._priority_for_depth(next_depth),
            )

    def _errback(self, failure):
        logger.debug("Request failed: %s", failure.request.url, exc_info=failure)
