import csv
import os
import tempfile
import unittest

from scraper import BooksParser, QuotesParser, save_csv

SAMPLE_QUOTE = """
<div class="quote">
  <span class="text">"Life is what happens to you while you're busy making other plans."</span>
  <span>by <small class="author">John Lennon</small></span>
  <div class="tags"><a class="tag">life</a></div>
</div>
"""

SAMPLE_BOOK = """
<article class="product_pod">
  <h3><a title="A Light in the Attic">A Light in the ...</a></h3>
  <p class="price_color">&pound;51.77</p>
</article>
"""


class QuotesParserTest(unittest.TestCase):
    def test_extracts_quote_fields(self):
        parser = QuotesParser()
        parser.feed(SAMPLE_QUOTE)
        self.assertEqual(len(parser.quotes), 1)
        quote = parser.quotes[0]
        self.assertIn("Life is what happens", quote["text"])
        self.assertEqual(quote["author"], "John Lennon")

    def test_ignores_empty_page(self):
        parser = QuotesParser()
        parser.feed("<html><body>nothing here</body></html>")
        self.assertEqual(parser.quotes, [])


class BooksParserTest(unittest.TestCase):
    def test_extracts_title_and_price(self):
        parser = BooksParser()
        parser.feed(SAMPLE_BOOK)
        self.assertEqual(len(parser.books), 1)
        self.assertEqual(parser.books[0]["title"], "A Light in the Attic")
        self.assertEqual(parser.books[0]["price"], "£51.77")


class SaveCsvTest(unittest.TestCase):
    def test_writes_header_and_rows(self):
        records = [{"text": "hello", "author": "me", "tags": "a"}]
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "out.csv")
            save_csv(records, path)
            with open(path, newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(rows, records)

    def test_empty_records_raise(self):
        with self.assertRaises(ValueError):
            save_csv([], "unused.csv")


if __name__ == "__main__":
    unittest.main()
