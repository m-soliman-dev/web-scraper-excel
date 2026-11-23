# web-scraper-excel

A Python command-line tool that collects data from websites and saves it to a
CSV spreadsheet that opens directly in Excel. No third-party packages needed -
it runs on any Python 3.8+ install.

## What it does

- Downloads pages from the public scraping practice sites
  ([quotes.toscrape.com](https://quotes.toscrape.com) and
  [books.toscrape.com](https://books.toscrape.com))
- Extracts structured data (quotes + authors, or book titles + prices)
- Saves everything to a clean `.csv` file, one row per record
- Sleeps politely between pages so it never hammers a server

## Usage

```bash
# Collect 3 pages of quotes into quotes.csv
python scraper.py quotes --pages 3 --output quotes.csv

# Collect 2 pages of book titles and prices
python scraper.py books --pages 2 --output books.csv
```

Open the resulting file in Excel (or Google Sheets) and every record is in its
own row with proper column headers.

## Why CSV?

CSV opens natively in Excel and Google Sheets, so there is nothing to install.
If you want a native `.xlsx` file, the same records can be written with the
optional `openpyxl` package.

## Running the tests

```bash
python -m unittest test_scraper.py -v
```

The tests parse saved sample pages, so they run offline.

## What I learned building this

- Parsing HTML with Python's built-in `html.parser`
- Writing well-formed CSV with correct encoding (`utf-8-sig` so Excel shows
  international characters properly)
- Structuring a small CLI with `argparse`
- Unit testing parsers against sample fixtures
