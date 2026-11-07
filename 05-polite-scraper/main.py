"""
The Polite Scraper - Assignment A9
Target: Books to Scrape (https://books.toscrape.com)
"""

from pathlib import Path
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/tahirkhan05/crud-api)"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT = 10
POLITE_DELAY = 0.5  # seconds between live web requests


def fetch_page(url: str, cache_filename: str) -> str:
    """Fetch HTML from local cache if it exists; otherwise fetch from live site politely and cache it."""
    cache_path = CACHE_DIR / cache_filename

    # Read from cache
    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        print(f"CACHE HIT: {cache_filename} ({len(html)} bytes)")
        return html

    # Wait at least 0.5s before hitting the live site (polite robot)
    time.sleep(POLITE_DELAY)

    # Fetch live from web
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url} (status {response.status_code})")

    html = response.text
    cache_path.write_text(html, encoding="utf-8")
    print(f"FETCH: {url} -> saved to {cache_filename} ({len(html)} bytes)")
    return html


def discover_books(start_url: str, max_pages: int = 3) -> list[str]:
    """Crawl up to max_pages catalogue pages and collect all book detail URLs."""
    current_url = start_url
    pages_crawled = 0
    discovered_urls = []

    while current_url and pages_crawled < max_pages:
        pages_crawled += 1
        cache_file = f"catalogue-page-{pages_crawled}.html"
        html = fetch_page(current_url, cache_file)

        soup = BeautifulSoup(html, "html.parser")

        # Collect book links from current page
        for link in soup.select("article.product_pod h3 a"):
            href = link.get("href")
            if href:
                absolute_url = urljoin(current_url, href)
                discovered_urls.append(absolute_url)

        # Follow "next" link if we have not reached max_pages
        next_button = soup.select_one("li.next a")
        if next_button and pages_crawled < max_pages:
            current_url = urljoin(current_url, next_button.get("href"))
        else:
            current_url = None

    # Deduplicate while preserving order
    unique_urls = list(dict.fromkeys(discovered_urls))

    print(
        f"catalogue_pages={pages_crawled}, discovered={len(discovered_urls)}, unique_urls={len(unique_urls)}"
    )
    return unique_urls


def main():
    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    discover_books(start_url, max_pages=3)


if __name__ == "__main__":
    main()
