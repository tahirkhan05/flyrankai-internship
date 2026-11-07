"""
The Polite Scraper - Assignment A9
Target: Books to Scrape (https://books.toscrape.com)
"""

from datetime import datetime, timezone
import json
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


def fetch_page(url: str, cache_filename: str) -> tuple[str, str]:
    """Fetch HTML from local cache if it exists; otherwise fetch from live site politely and cache it.
    Returns a tuple of (html_content, fetched_at_iso_timestamp).
    """
    cache_path = CACHE_DIR / cache_filename

    # Read from cache
    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        fetched_at = datetime.fromtimestamp(
            cache_path.stat().st_mtime, timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"CACHE HIT: {cache_filename} ({len(html)} bytes)")
        return html, fetched_at

    # Wait at least 0.5s before hitting the live site (polite robot)
    time.sleep(POLITE_DELAY)

    # Fetch live from web
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url} (status {response.status_code})")

    response.encoding = "utf-8"
    html = response.text
    cache_path.write_text(html, encoding="utf-8")
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"FETCH: {url} -> saved to {cache_filename} ({len(html)} bytes)")
    return html, fetched_at


def discover_books(start_url: str, max_pages: int = 3) -> dict[str, str]:
    """Crawl up to max_pages catalogue pages and collect all unique book detail URLs.
    Returns a dict mapping {book_url: source_catalogue_page}.
    """
    current_url = start_url
    pages_crawled = 0
    total_discovered = 0
    discovered_books = {}  # url -> source_page

    while current_url and pages_crawled < max_pages:
        pages_crawled += 1
        cache_file = f"catalogue-page-{pages_crawled}.html"
        html, _ = fetch_page(current_url, cache_file)

        soup = BeautifulSoup(html, "html.parser")

        # Collect book links from current page
        for link in soup.select("article.product_pod h3 a"):
            href = link.get("href")
            if href:
                absolute_url = urljoin(current_url, href)
                total_discovered += 1
                if absolute_url not in discovered_books:
                    discovered_books[absolute_url] = current_url

        # Follow "next" link if we have not reached max_pages
        next_button = soup.select_one("li.next a")
        if next_button and pages_crawled < max_pages:
            current_url = urljoin(current_url, next_button.get("href"))
        else:
            current_url = None

    print(
        f"catalogue_pages={pages_crawled}, discovered={total_discovered}, unique_urls={len(discovered_books)}"
    )
    return discovered_books


def extract_book_details(
    html: str, product_url: str, source_page: str, fetched_at: str
) -> dict:
    """Extract the 8 required raw fields from a book's detail page."""
    soup = BeautifulSoup(html, "html.parser")
    product_page = soup.select_one("article.product_page")

    # 1. title
    title_tag = product_page.select_one("h1") if product_page else None
    title = title_tag.get_text(strip=True) if title_tag else ""

    # 2. product_url (canonical URL)

    # 3. price_text
    price_tag = product_page.select_one("p.price_color") if product_page else None
    price_text = price_tag.get_text(strip=True) if price_tag else ""

    # 4. availability_text
    avail_tag = product_page.select_one("p.availability") if product_page else None
    availability_text = avail_tag.get_text(strip=True) if avail_tag else ""

    # 5. rating_text
    rating_tag = product_page.select_one("p.star-rating") if product_page else None
    rating_classes = rating_tag.get("class", []) if rating_tag else []
    star_classes = [c for c in rating_classes if c != "star-rating"]
    rating_text = star_classes[0] if star_classes else ""

    # 6. description (null if absent)
    desc_header = soup.select_one("#product_description")
    if desc_header:
        desc_p = desc_header.find_next_sibling("p")
        description = desc_p.get_text(strip=True) if desc_p else None
    else:
        description = None

    # 7. source_page (receipt / provenance)
    # 8. fetched_at (receipt / provenance)

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }


def main():
    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    books = discover_books(start_url, max_pages=3)

    raw_records = []
    for url, source_page in books.items():
        slug = url.rstrip("/").split("/")[-2]
        cache_file = f"book-{slug}.html"
        html, fetched_at = fetch_page(url, cache_file)
        record = extract_book_details(html, url, source_page, fetched_at)
        raw_records.append(record)

    # Checkpoint Stage 3: print one complete raw record and summary
    if raw_records:
        print("\nSample Raw Record:")
        print(json.dumps(raw_records[0], indent=2, ensure_ascii=False))
    print(f"\ndetail_pages={len(raw_records)}")


if __name__ == "__main__":
    main()
