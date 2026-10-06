from __future__ import annotations

import argparse
import csv
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import deduplicate
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper, ScraperConfig
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"

FIELDS = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "availability",
    "scraped_at",
]


def setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def scrape_source(name: str, scraper) -> tuple[list[dict], int]:
    logger = logging.getLogger(__name__)
    records: list[dict] = []
    failures = 0

    try:
        for record in scraper.scrape():
            records.append(record)
    except Exception:
        failures += 1
        logger.exception("Unexpected failure while scraping %s", name)

    return records, failures


def write_csv(records: list[dict]) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def run(delay: float) -> dict:
    start = time.perf_counter()
    scraped_at = datetime.now(timezone.utc).isoformat()

    config = ScraperConfig(delay_seconds=delay)
    books, books_failures = scrape_source("Books to Scrape", BooksScraper(config))
    quotes, quotes_failures = scrape_source(
        "Quotes to Scrape", QuotesScraper(delay_seconds=delay)
    )

    raw_records = books + quotes

    cleaned_records = []
    validation_rejected = 0
    validation_errors: dict[str, int] = {}

    for raw in raw_records:
        record = clean_record(raw)
        record["scraped_at"] = scraped_at

        valid, errors = validate_record(record)
        if not valid:
            validation_rejected += 1
            for error in errors:
                validation_errors[error] = validation_errors.get(error, 0) + 1
            continue

        cleaned_records.append(record)

    unique_records, duplicate_count = deduplicate(cleaned_records)
    write_csv(unique_records)

    by_source_raw = {
        "Books to Scrape": len(books),
        "Quotes to Scrape": len(quotes),
    }
    by_source_final: dict[str, int] = {}
    for record in unique_records:
        source = record["source"]
        by_source_final[source] = by_source_final.get(source, 0) + 1

    elapsed = round(time.perf_counter() - start, 3)
    summary = {
        "generated_at": scraped_at,
        "records_collected_per_source": by_source_raw,
        "total_records_collected": len(raw_records),
        "total_records_after_cleaning_and_validation": len(cleaned_records),
        "records_rejected_during_validation": validation_rejected,
        "validation_errors": validation_errors,
        "duplicate_records_detected_or_removed": duplicate_count,
        "final_record_count": len(unique_records),
        "final_records_per_source": by_source_final,
        "source_failures": {
            "Books to Scrape": books_failures,
            "Quotes to Scrape": quotes_failures,
        },
        "execution_time_seconds": elapsed,
        "output_file": str(CSV_PATH.relative_to(ROOT)),
        "log_file": str(LOG_PATH.relative_to(ROOT)),
    }

    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-source web scraping pipeline")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.2,
        help="Delay between requests in seconds (default: 0.2)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    setup_logging()
    args = parse_args()
    result = run(delay=args.delay)
    print(json.dumps(result, indent=2))
