from __future__ import annotations

import logging
import time
from typing import Iterator, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://quotes.toscrape.com/"
USER_AGENT = "Python-Web-Scraping-Interview-Assignment/1.0"


class QuotesScraper:
    """Scraper for Quotes to Scrape with automatic pagination."""

    def __init__(self, timeout: int = 15, delay_seconds: float = 0.2, max_retries: int = 3):
        self.timeout = timeout
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def _get(self, url: str) -> Optional[requests.Response]:
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                LOGGER.warning(
                    "Quotes request failed (attempt %s/%s): %s",
                    attempt,
                    self.max_retries,
                    exc,
                )
                if attempt < self.max_retries:
                    time.sleep(2 ** (attempt - 1))
        LOGGER.error("Giving up on URL: %s", url)
        return None

    def scrape(self) -> Iterator[dict]:
        next_url = BASE_URL

        while next_url:
            LOGGER.info("Scraping Quotes page: %s", next_url)
            response = self._get(next_url)
            if not response:
                return

            soup = BeautifulSoup(response.text, "html.parser")
            quote_nodes = soup.select("div.quote")

            if not quote_nodes:
                LOGGER.warning("No quote records found on %s", next_url)

            for node in quote_nodes:
                text_node = node.select_one("span.text")
                author_node = node.select_one("small.author")
                tag_nodes = node.select("div.tags a.tag")

                if not text_node:
                    LOGGER.warning("Skipping quote with missing text on %s", next_url)
                    continue

                author = author_node.get_text(" ", strip=True) if author_node else None
                tags = [tag.get_text(" ", strip=True) for tag in tag_nodes]

                author_url = None
                if author_node:
                    author_link = node.select_one("span a")
                    if author_link and author_link.get("href"):
                        author_url = urljoin(next_url, author_link["href"])

                yield {
                    "source": "Quotes to Scrape",
                    "source_url": next_url,
                    "name_or_title": text_node.get_text(" ", strip=True),
                    "category": None,
                    "price": None,
                    "rating": None,
                    "author": author,
                    "tags": ", ".join(tags) if tags else None,
                    "description": None,
                    "availability": None,
                    "author_url": author_url,
                }

            next_link = soup.select_one("li.next a")
            next_url = urljoin(next_url, next_link.get("href")) if next_link else None
            time.sleep(self.delay_seconds)
