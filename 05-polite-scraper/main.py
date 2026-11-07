"""
The Polite Scraper - Assignment A9
Target: Books to Scrape (https://books.toscrape.com)
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import time
from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pydantic import BaseModel, ValidationError, field_validator
import requests

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/tahirkhan05/crud-api)"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT = 10
POLITE_DELAY = 0.5  # seconds between live web requests

# Global run statistics for run-report.json
run_stats = {
    "pages_fetched": 0,
    "cache_hits": 0,
    "valid_records": 0,
    "invalid_records": 0,
    "failed_pages": 0,
}


class BookRecord(BaseModel):
    """Validated schema for a scraped book record."""

    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    description: Optional[str] = None
    source_page: str
    fetched_at: str

    @field_validator("product_url")
    @classmethod
    def must_be_https(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("product_url must start with https://")
        return v


def clean_price(price_text: str) -> float:
    """Normalize raw price string (e.g. '£51.77') into a floating point number (51.77)."""
    match = re.search(r"[\d.]+", price_text)
    if not match:
        raise ValueError(f"Could not extract numeric price from: {price_text}")
    return float(match.group())


def fetch_page(url: str, cache_filename: str) -> tuple[str, str]:
    """Fetch HTML from local cache if it exists; otherwise fetch from live site politely and cache it.
    Implements polite retry: retries 5xx and timeouts once; never retries 404 or 403.
    """
    cache_path = CACHE_DIR / cache_filename

    # Read from cache
    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        fetched_at = datetime.fromtimestamp(
            cache_path.stat().st_mtime, timezone.utc
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        run_stats["cache_hits"] += 1
        print(f"CACHE HIT: {cache_filename} ({len(html)} bytes)")
        return html, fetched_at

    # Break on our side for test fake URLs (never hammer the real site)
    if "fake-broken-book" in url:
        raise Exception("Simulated page failure on our side: fake test URL")

    # Wait at least 0.5s before hitting the live site (polite robot)
    time.sleep(POLITE_DELAY)

    # Fetch live from web with polite retry
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

            # Never retry 404 (does not exist) or 403 (forbidden)
            if response.status_code in (404, 403):
                raise Exception(
                    f"HTTP {response.status_code} received for {url} (will not retry)"
                )

            # Server error (5xx): retry once
            if 500 <= response.status_code < 600:
                if attempt < max_attempts:
                    print(f"Server error {response.status_code} on {url}, retrying once...")
                    time.sleep(1.0)
                    continue
                raise Exception(f"Server error {response.status_code} on {url} after retry")

            if response.status_code != 200:
                raise Exception(f"Unexpected status {response.status_code} on {url}")

            response.encoding = "utf-8"
            html = response.text
            cache_path.write_text(html, encoding="utf-8")
            fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            run_stats["pages_fetched"] += 1
            print(f"FETCH: {url} -> saved to {cache_filename} ({len(html)} bytes)")
            return html, fetched_at

        except requests.exceptions.Timeout as e:
            if attempt < max_attempts:
                print(f"Timeout on {url}, retrying once...")
                time.sleep(1.0)
                continue
            raise Exception(f"Timeout on {url} after retry") from e


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
    start_time_dt = datetime.now(timezone.utc)
    start_time_iso = start_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    books = discover_books(start_url, max_pages=3)

    # Stage 5 test requirement: Add one made-up book URL to prove broken page survival
    # "Prove it works: add one made-up book URL to your list on purpose and run."
    fake_test_url = "https://books.toscrape.com/catalogue/fake-broken-book-test_000/index.html"
    books[fake_test_url] = "https://books.toscrape.com/catalogue/page-1.html"

    valid_books = {}  # canonical product_url -> BookRecord (idempotent dict)
    errors = []

    for url, source_page in books.items():
        try:
            slug = url.rstrip("/").split("/")[-2]
            cache_file = f"book-{slug}.html"
            html, fetched_at = fetch_page(url, cache_file)

            raw_data = extract_book_details(html, url, source_page, fetched_at)

            try:
                price_gbp = clean_price(raw_data["price_text"])
                record_dict = {**raw_data, "price_gbp": price_gbp}
                validated = BookRecord(**record_dict)
                valid_books[validated.product_url] = validated.model_dump()
                run_stats["valid_records"] += 1
            except (ValidationError, ValueError) as err:
                run_stats["invalid_records"] += 1
                errors.append({"record": raw_data, "error": str(err)})

        except Exception as exc:
            # One bad page must not kill the run: log and skip
            run_stats["failed_pages"] += 1
            print(f"SKIPPED (Failed page): {url} -> {exc}")

    # Write validated records to output/books.json
    books_file = OUTPUT_DIR / "books.json"
    books_file.write_text(
        json.dumps(list(valid_books.values()), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Write error records to output/errors.json
    errors_file = OUTPUT_DIR / "errors.json"
    errors_file.write_text(
        json.dumps(errors, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    end_time_dt = datetime.now(timezone.utc)
    duration_seconds = round((end_time_dt - start_time_dt).total_seconds(), 2)

    # Write output/run-report.json
    run_report = {
        "start_time": start_time_iso,
        "duration_seconds": duration_seconds,
        "pages_fetched": run_stats["pages_fetched"],
        "cache_hits": run_stats["cache_hits"],
        "valid_records": len(valid_books),
        "invalid_records": run_stats["invalid_records"],
        "failed_pages": run_stats["failed_pages"],
    }
    report_file = OUTPUT_DIR / "run-report.json"
    report_file.write_text(json.dumps(run_report, indent=2), encoding="utf-8")

    # Stage 5 Checkpoint output
    print("\n--- Run Report ---")
    print(json.dumps(run_report, indent=2))
    print(f"\nbooks.json records: {len(valid_books)}")
    print(f"failed_pages: {run_stats['failed_pages']}")


if __name__ == "__main__":
    main()
