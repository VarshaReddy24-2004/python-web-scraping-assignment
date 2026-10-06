from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlparse


def clean_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    value = re.sub(r"\s+", " ", str(value)).strip()
    return value or None


def normalize_key(value: Any) -> str:
    text = clean_text(value) or ""
    return text.casefold()


def parse_price(value: Any) -> Optional[float]:
    if value is None:
        return None
    match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value).replace(",", ""))
    return float(match.group()) if match else None


def normalize_rating(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        rating = float(value)
    except (TypeError, ValueError):
        return None
    return rating if 0 <= rating <= 5 else None


def normalize_url(value: Any) -> Optional[str]:
    value = clean_text(value)
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    return None


def clean_record(record: dict) -> dict:
    cleaned = dict(record)

    for key in (
        "source",
        "source_url",
        "name_or_title",
        "category",
        "author",
        "tags",
        "description",
        "availability",
        "author_url",
    ):
        if key in cleaned:
            cleaned[key] = clean_text(cleaned[key])

    cleaned["source_url"] = normalize_url(cleaned.get("source_url"))
    if "author_url" in cleaned:
        cleaned["author_url"] = normalize_url(cleaned.get("author_url"))

    cleaned["price"] = parse_price(cleaned.get("price"))
    cleaned["rating"] = normalize_rating(cleaned.get("rating"))

    return cleaned
