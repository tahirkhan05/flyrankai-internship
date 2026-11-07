# The Polite Scraper

FlyRank AI Internship · AI Backend Engineer · Assignment A5 (A9)

A small, reliable, polite web scraping pipeline built in Python: downloads the first three catalogue pages of Books to Scrape, visits all 60 book pages, normalizes messy HTML into clean, validated JSON records, survives broken pages without crashing, and generates an honest run report.

---

## 1. Target Classification

* **Target Site**: Books to Scrape (`https://books.toscrape.com`)
* **Purpose & Permission**: `toscrape.com` explicitly notes that Books to Scrape is a dedicated practice sandbox built for developers to learn and practice web scraping. This explicit public purpose is our permission.
* **Scope**: Exactly the first **3 catalogue pages** (`page-1.html`, `page-2.html`, `page-3.html`), totaling **60 unique books**.
* **Data Collected**: Book title, canonical product URL, raw price text, normalized numeric price (GBP), availability text, star rating, product description, source page provenance, and fetch timestamp.
* **Robots.txt Analysis**: Requested `https://books.toscrape.com/robots.txt` $\rightarrow$ returned HTTP status `404` (**no robots file found**). A missing robots.txt is not blanket permission; our scope is constrained because we respect server resources.
* **Core Rule**: *"I will not reuse this code on another site without checking its rules and terms first."*

---

## 2. Lane & Installation

* **Lane**: Python 3.10+
* **Dependencies**: `requests`, `beautifulsoup4`, `pydantic`

### Installation

```bash
cd 05-polite-scraper
pip install -r requirements.txt
```

---

## 3. One Run Command

To run the full scraper pipeline:

```bash
python main.py
```

Running the command will:
1. Crawl catalogue pages 1 through 3 via relative link resolution (`urljoin`).
2. Deduplicate book URLs (exactly 60 unique books).
3. Fetch detail pages with polite rate limiting, storing raw HTML into `cache/`.
4. Normalize and validate records with Pydantic into `output/books.json`.
5. Isolate invalid records into `output/errors.json`.
6. Survive broken or fake pages gracefully and produce `output/run-report.json`.

---

## 4. Record Schema

The schema is enforced using **Pydantic**:

```python
from pydantic import BaseModel, field_validator
from typing import Optional

class BookRecord(BaseModel):
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
```

### Sample Validated Output (`output/books.json`)

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "£51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": "It's hard to imagine a world without A Light in the Attic...",
  "source_page": "https://books.toscrape.com/catalogue/page-1.html",
  "fetched_at": "2026-11-07T21:10:22Z"
}
```

---

## 5. Politeness Rules

1. **Honest User-Agent**: Every request identifies the crawler with a contact link:
   `FlyRankInternship-A9/1.0 (+https://github.com/tahirkhan05/flyrankai-internship)`
2. **Polite Delay**: Enforces at least `500 ms` delay (`time.sleep(0.5)`) between live HTTP requests to avoid hammering the site.
3. **Local Cache First**: Every HTML page is saved to `cache/`. Subsequent runs use `CACHE HIT` with zero network requests and zero latency.
4. **Timeout Enforced**: Every network request caps at `10s` (`timeout=10`) so the crawler never hangs indefinitely.
5. **Polite Retries**: Retries 5xx server errors and network timeouts once after a 1.0s pause. It **never retries 404** (page does not exist) or **403** (forbidden), avoiding becoming a nuisance.

---

## 6. Real Run Report (`output/run-report.json`)

```json
{
  "start_time": "2026-11-07T21:15:37Z",
  "duration_seconds": 1.05,
  "pages_fetched": 0,
  "cache_hits": 63,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}
```

> **Why no browser was needed**: This assignment needed no browser because the data is already in the HTML the server sends, so a browser would only add cost.

---

## 7. Honest Limitation

This scraper assumes static HTML responses. If Books to Scrape migrated to a client-rendered Single Page Application (e.g. React or Vue) where product details are injected dynamically by client-side JavaScript, `requests` and `BeautifulSoup` would only download an empty template shell without product listings.

---

## 8. Ethics Note

Always use an official API when one exists. Never attempt to bypass authentication logins, CAPTCHAs, paywalls, or blocking mechanisms. Respect the site owner's bandwidth and terms of service, and collect only what is strictly necessary.
