# Python Web Scraping Interview Assignment

## 1. Overview

This project implements a reusable multi-source web scraping and data-processing pipeline for:

- Books to Scrape: https://books.toscrape.com/
- Quotes to Scrape: https://quotes.toscrape.com/

The pipeline performs:

1. Scraping
2. Pagination
3. Cleaning and standardization
4. Validation
5. Duplicate detection
6. Consolidation
7. CSV generation
8. JSON summary generation
9. Logging and error handling

The design follows the assignment requirement to keep source-specific parsing separate from common processing logic.

## 2. Python Version

Recommended: Python 3.10+.

## 3. Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 4. Run

From the project root:

```bash
python main.py
```

Optional request delay:

```bash
python main.py --delay 0.5
```

The default delay is deliberately modest so the scraper does not make unnecessarily aggressive requests.

## 5. Pagination

Both scrapers discover the next page using the site's `li.next a` link.

The code does not hard-code a fixed number of pages. It keeps requesting pages until the source has no next-page link.

## 6. Data Model

The consolidated CSV contains:

- `source`
- `source_url`
- `name_or_title`
- `category`
- `price`
- `rating`
- `author`
- `tags`
- `description`
- `availability`
- `scraped_at`

Fields that do not apply to a source are stored as empty/null values. No values are invented.

## 7. Cleaning

`processing/cleaning.py` contains reusable transformations:

- whitespace cleanup
- case-insensitive normalization for duplicate keys
- price conversion to numeric values
- rating normalization to a 0–5 numeric value
- basic HTTP/HTTPS URL validation
- missing-value handling

## 8. Validation

`processing/validation.py` checks:

- source is present
- source URL exists and looks valid
- title/text is present
- price is numeric and non-negative when present
- rating is numeric and within 0–5 when present

Invalid records are rejected and their validation errors are counted in the summary.

## 9. Duplicate Detection

`processing/deduplication.py` uses a normalized SHA-256 key.

The source URL is the primary identity. A fallback key uses normalized source + title + author. This avoids treating harmless whitespace/capitalization differences as separate records.

Duplicates are removed from the final dataset and counted in `summary_report.json`.

## 10. Error Handling

The scrapers handle:

- connection errors
- HTTP errors
- timeouts
- missing selectors
- unexpected/missing values
- individual request failures

Requests are retried with exponential backoff. A failed page/source is logged and the application avoids crashing the entire pipeline unnecessarily.

## 11. Output

After execution:

```text
output/
├── final_dataset.csv
└── summary_report.json
```

Logs:

```text
logs/
└── scraper.log
```

The summary includes:

- total records collected per source
- total records after cleaning/validation
- validation rejections
- duplicate count
- final record count
- final count by source
- source failures
- execution time

## 12. Tests

Run:

```bash
python -m unittest discover -s tests -v
```

The tests cover price conversion, rating validation, cleaning, validation, and duplicate detection.

## 13. Project Structure

```text
scraping_assignment/
├── scrapers/
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── cleaning.py
│   ├── validation.py
│   └── deduplication.py
├── output/
├── logs/
├── tests/
│   └── test_processing.py
├── main.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## 14. Assumptions

- The two provided practice sites remain publicly accessible.
- Their basic HTML structures remain compatible with the selectors in this project.
- A source URL is an acceptable primary identity for duplicate detection.
- Quote-specific fields such as author/tags are not forced into book records.
- Book-specific fields such as price/rating are left empty for quote records.

## 15. Known Limitations

- The implementation depends on the current HTML structure of the practice sites.
- It is not intended to be a production-scale distributed crawler.
- It does not bypass CAPTCHA, authentication, robots restrictions, or access controls.
- It does not persist crawl state between executions.
- It does not use a database because the assignment only requires a consolidated CSV and summary report.

## 16. AI Usage

See `AI_USAGE.md`. The assignment explicitly permits AI assistance, but the submitted implementation should be reviewed and understood by the candidate.
