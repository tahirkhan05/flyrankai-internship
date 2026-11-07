# The Polite Scraper

FlyRank Internship Backend Track · Week 5 · Assignment A9

A reliable, polite web scraping pipeline built in Python: downloads the first three catalogue pages of Books to Scrape, visits all 60 book pages, normalizes messy HTML into clean JSON records, survives broken pages, and generates an honest run report.

---

## Target Classification

* **Target Site**: Books to Scrape (`https://books.toscrape.com`)
* **Purpose & Permission**: `toscrape.com` explicitly declares that Books to Scrape is a dedicated practice sandbox built for developers to learn and test web scraping. This explicit public purpose serves as our authorization.
* **Scope**: Exactly the first **3 catalogue pages** (`page-1.html`, `page-2.html`, `page-3.html`), totaling **60 unique books**.
* **Data Collected**: Book title, product URL, price, availability status, star rating, product description, source page provenance, and fetch timestamp.
* **Robots.txt Analysis**: Requested `https://books.toscrape.com/robots.txt` $\rightarrow$ returned HTTP status `404` (**no robots file found**). A missing robots.txt is not permission by itself; our scope is constrained because we respect site resources.
* **Guiding Principle**: *"I will not reuse this code on another site without checking its rules and terms first."*

---

## Politeness Rules Followed

1. **Honest User-Agent**: Every HTTP request identifies the scraper (`FlyRankInternship-A9/1.0 (+https://github.com/tahirkhan05/crud-api)`).
2. **Rate Limiting**: Waits at least 500 ms between live network requests to prevent server strain.
3. **Local Caching**: Every fetched HTML page is saved locally to `cache/`. Subsequent runs read from local cache (`CACHE HIT`) rather than re-requesting the site.
4. **Timeout Enforced**: Requests timeout after 10 seconds rather than hanging indefinitely.

---

## Quickstart

```bash
cd 05-polite-scraper
pip install -r requirements.txt
python main.py
```

