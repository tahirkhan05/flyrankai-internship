"""
The Polite Scraper - Assignment A9
Target: Books to Scrape (https://books.toscrape.com)
"""

from pathlib import Path
import requests

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/tahirkhan05/crud-api)"
HEADERS = {"User-Agent": USER_AGENT}
TIMEOUT = 10


def fetch_page(url: str, cache_filename: str) -> str:
    """Fetch HTML from local cache if it exists; otherwise fetch from live site and cache it."""
    cache_path = CACHE_DIR / cache_filename

    # Read from cache
    if cache_path.exists():
        html = cache_path.read_text(encoding="utf-8")
        print(f"CACHE HIT: {cache_filename} ({len(html)} bytes)")
        return html

    # Fetch live from web
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url} (status {response.status_code})")

    html = response.text
    cache_path.write_text(html, encoding="utf-8")
    print(f"FETCH: {url} -> saved to {cache_filename} ({len(html)} bytes)")
    return html


def main():
    first_page_url = "https://books.toscrape.com/catalogue/page-1.html"
    fetch_page(first_page_url, "catalogue-page-1.html")


if __name__ == "__main__":
    main()

