from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Iterator, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger(__name__)

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = urljoin(BASE_URL, "catalogue/")
USER_AGENT = "Python-Web-Scraping-Interview-Assignment/1.0"


@dataclass
class ScraperConfig:
    timeout: int = 5
    delay_seconds: float = 0.2
    max_retries: int = 2


class BooksScraper:
    """Scraper for Books to Scrape.

    Pagination is discovered from each page's 'next' link instead of
    hard-coding a fixed number of pages.
    """

    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def _get(self, url: str) -> Optional[requests.Response]:
        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = self.session.get(url, timeout=self.config.timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                LOGGER.warning(
                    "Books request failed (attempt %s/%s): %s",
                    attempt,
                    self.config.max_retries,
                    exc,
                )
                if attempt < self.config.max_retries:
                    time.sleep(2 ** (attempt - 1))
        LOGGER.error("Giving up on URL: %s", url)
        return None

    @staticmethod
    def _rating_to_number(value: str) -> Optional[float]:
        mapping = {"One": 1.0, "Two": 2.0, "Three": 3.0, "Four": 4.0, "Five": 5.0}
        return mapping.get(value)

    def _parse_detail(self, url: str) -> tuple[Optional[str], Optional[str]]:
        response = self._get(url)
        if not response:
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")
        category = None
        description = None

        breadcrumb = soup.select("ul.breadcrumb li a")
        if len(breadcrumb) >= 3:
            category = breadcrumb[-1].get_text(" ", strip=True)

        description_node = soup.select_one("#product_description + p")
        if description_node:
            description = description_node.get_text(" ", strip=True)

        time.sleep(self.config.delay_seconds)
        return category, description

    def scrape(self) -> Iterator[dict]:
        next_url = urljoin(BASE_URL, "catalogue/page-1.html")

        while next_url:
            LOGGER.info("Scraping Books page: %s", next_url)
            response = self._get(next_url)
            if not response:
                # Continue is not possible without a page link, so stop this source
                # cleanly rather than stopping the whole application.
                return

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select("article.product_pod")

            if not cards:
                LOGGER.warning("No book cards found on %s", next_url)

            for card in cards:
                title_node = card.select_one("h3 a")
                price_node = card.select_one(".price_color")
                availability_node = card.select_one(".availability")
                rating_node = card.select_one("p.star-rating")

                if not title_node:
                    LOGGER.warning("Skipping book with missing title on %s", next_url)
                    continue

                relative_url = title_node.get("href", "")
                product_url = urljoin(next_url, relative_url)
                title = title_node.get("title") or title_node.get_text(" ", strip=True)

                rating_class = ""
                if rating_node:
                    classes = rating_node.get("class", [])
                    rating_class = next(
                        (item for item in classes if item != "star-rating"), ""
                    )

                category, description = self._parse_detail(product_url)

                yield {
                    "source": "Books to Scrape",
                    "source_url": product_url,
                    "name_or_title": title,
                    "category": category,
                    "price": price_node.get_text(" ", strip=True)
                    if price_node
                    else None,
                    "rating": self._rating_to_number(rating_class),
                    "author": None,
                    "tags": None,
                    "description": description,
                    "availability": availability_node.get_text(" ", strip=True)
                    if availability_node
                    else None,
                }

            next_link = soup.select_one("li.next a")
            next_url = urljoin(next_url, next_link.get("href")) if next_link else None
            time.sleep(self.config.delay_seconds)
