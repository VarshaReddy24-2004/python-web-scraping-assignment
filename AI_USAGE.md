# AI_USAGE.md

## Tool Used

Tool: ChatGPT

## What AI Was Used For

ChatGPT was used to assist with:

- designing the project structure
- planning the standardized data model
- drafting Requests + BeautifulSoup scraping logic
- implementing pagination
- designing cleaning and validation functions
- designing duplicate-detection logic
- adding retry/error handling and logging
- creating unit tests
- drafting README documentation

## Representative Prompts

1. "Create a Python Requests and BeautifulSoup scraper for Books to Scrape that discovers pagination instead of hard-coding page numbers."
2. "Create a separate scraper for Quotes to Scrape and normalize its fields into a common schema."
3. "Add reusable cleaning, validation, and duplicate-detection functions for a multi-source scraper."
4. "Add retries, logging, and tests for the scraping pipeline."
5. "Create README documentation covering setup, pagination, validation, deduplication, outputs, assumptions, and limitations."

## AI-Assisted Parts

The following files were AI-assisted:

- `main.py`
- `scrapers/books_scraper.py`
- `scrapers/quotes_scraper.py`
- `processing/cleaning.py`
- `processing/validation.py`
- `processing/deduplication.py`
- `tests/test_processing.py`
- `README.md`

## Review and Verification

The implementation should be reviewed by the candidate before submission. In particular, selectors should be checked against the live public practice sites, the generated CSV should be inspected, and tests should be run from a clean virtual environment.

## Important Corrections / Decisions

- Source-specific fields are not fabricated when they do not apply.
- Pagination is link-driven rather than based on a fixed page count.
- Validation rejects clearly invalid records instead of silently writing them.
- Duplicate detection is based on normalized identity information.
- Retry behavior uses exponential backoff.
- The scraper intentionally avoids bypassing authentication, CAPTCHA, access controls, or other security mechanisms.

## Testing

Run:

```bash
python -m unittest discover -s tests -v
```

Then run:

```bash
python main.py
```

Finally inspect:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`
