import unittest

from processing.cleaning import clean_record, parse_price, normalize_rating
from processing.deduplication import deduplicate
from processing.validation import validate_record


class ProcessingTests(unittest.TestCase):
    def test_parse_price(self):
        self.assertEqual(parse_price("£51.77"), 51.77)

    def test_normalize_rating(self):
        self.assertEqual(normalize_rating("5"), 5.0)
        self.assertIsNone(normalize_rating("7"))

    def test_clean_record(self):
        record = clean_record(
            {
                "source": " Books to Scrape ",
                "source_url": " https://books.toscrape.com/catalogue/a_1/index.html ",
                "name_or_title": "  Example Book  ",
                "price": "£10.50",
                "rating": "4",
            }
        )
        self.assertEqual(record["name_or_title"], "Example Book")
        self.assertEqual(record["price"], 10.50)
        self.assertEqual(record["rating"], 4.0)

    def test_validation(self):
        valid, errors = validate_record(
            {
                "source": "Books to Scrape",
                "source_url": "https://books.toscrape.com/",
                "name_or_title": "Example",
                "price": 10.0,
                "rating": 4.0,
            }
        )
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_deduplication(self):
        records = [
            {
                "source": "Books to Scrape",
                "source_url": "https://books.toscrape.com/a",
                "name_or_title": "Example",
            },
            {
                "source": "Books to Scrape",
                "source_url": "https://books.toscrape.com/a",
                "name_or_title": "Example",
            },
        ]
        unique, duplicates = deduplicate(records)
        self.assertEqual(len(unique), 1)
        self.assertEqual(duplicates, 1)


if __name__ == "__main__":
    unittest.main()
