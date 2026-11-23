#!/usr/bin/env python3
"""web-scraper-excel - pull data from websites and save it to a spreadsheet.

Scrapes practice sites (quotes.toscrape.com / books.toscrape.com) or any page
you point it at, and saves the results to CSV, which opens directly in Excel.

Usage:
    python scraper.py quotes --pages 3 --output quotes.csv
    python scraper.py books --pages 2 --output books.csv
"""

import argparse
import csv
import sys
import time
from html.parser import HTMLParser
from urllib.request import Request, urlopen

USER_AGENT = "web-scraper-excel/1.0 (+https://github.com/m-soliman-dev/web-scraper-excel)"


def fetch(url):
    """Download a page and return its HTML as text."""
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8", errors="replace")


class QuotesParser(HTMLParser):
    """Extract quotes, authors and tags from quotes.toscrape.com pages."""

    def __init__(self):
        super().__init__()
        self.quotes = []
        self._current = None
        self._capture = None

    def handle_starttag(self, tag, attrs):
        classes = dict(attrs).get("class", "")
        if tag == "div" and "quote" in classes.split():
            self._current = {"text": "", "author": "", "tags": ""}
        elif self._current is not None:
            if tag == "span" and "text" in classes.split():
                self._capture = "text"
            elif tag == "small" and "author" in classes.split():
                self._capture = "author"
            elif tag == "a" and "tag" in classes.split():
                self._capture = "tag"

    def handle_endtag(self, tag):
        if self._capture == "text" and tag == "span":
            self._capture = None
        elif self._capture == "author" and tag == "small":
            self._capture = None
        elif self._capture == "tag" and tag == "a":
            self._capture = None
        elif tag == "div" and self._current is not None and self._current["text"]:
            self.quotes.append(self._current)
            self._current = None

    def handle_data(self, data):
        if self._current is None or not self._capture:
            return
        text = data.strip()
        if not text:
            return
        if self._capture == "tag":
            self._current["tags"] = (self._current["tags"] + ", " + text
                                     if self._current["tags"] else text)
        else:
            self._current[self._capture] += text


class BooksParser(HTMLParser):
    """Extract titles and prices from books.toscrape.com pages."""

    def __init__(self):
        super().__init__()
        self.books = []
        self._capture = None
        self._current = None

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        classes = attr.get("class", "")
        if tag == "article" and "product_pod" in classes.split():
            self._current = {"title": "", "price": ""}
        elif self._current is not None:
            if tag == "h3":
                self._capture = "title"
            elif tag == "p" and "price_color" in classes.split():
                self._capture = "price"
            elif tag == "a" and self._capture == "title" and attr.get("title"):
                self._current["title"] = attr["title"]

    def handle_endtag(self, tag):
        if tag == "article" and self._current is not None:
            self.books.append(self._current)
            self._current = None
        elif self._capture == "title" and tag == "h3":
            self._capture = None
        elif self._capture == "price" and tag == "p":
            self._capture = None

    def handle_data(self, data):
        if self._current is not None and self._capture == "price":
            self._current["price"] += data.strip()


def scrape(kind, pages):
    """Scrape `pages` pages of the chosen practice site and return records."""
    records = []
    base = {"quotes": "https://quotes.toscrape.com/page/{}/",
            "books": "https://books.toscrape.com/catalogue/page-{}.html"}[kind]
    parser_class = {"quotes": QuotesParser, "books": BooksParser}[kind]
    for page in range(1, pages + 1):
        html = fetch(base.format(page))
        parser = parser_class()
        parser.feed(html)
        batch = parser.quotes if kind == "quotes" else parser.books
        print(f"page {page}: {len(batch)} {kind}")
        records.extend(batch)
        if page < pages:
            time.sleep(1)  # be polite to the server
    return records


def save_csv(records, path):
    """Save a list of dicts to a CSV file (opens directly in Excel)."""
    if not records:
        raise ValueError("nothing scraped - check the site and page count")
    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("kind", choices=["quotes", "books"],
                        help="what to scrape from the practice sites")
    parser.add_argument("--pages", type=int, default=1,
                        help="number of pages to scrape (default: 1)")
    parser.add_argument("--output", default="data.csv",
                        help="output CSV file (default: data.csv)")
    args = parser.parse_args()

    try:
        records = scrape(args.kind, args.pages)
        save_csv(records, args.output)
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"saved {len(records)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
