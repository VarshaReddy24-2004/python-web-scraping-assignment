from __future__ import annotations

from urllib.parse import urlparse


def validate_record(record: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not record.get("source"):
        errors.append("missing_source")

    if not record.get("source_url"):
        errors.append("missing_source_url")
    else:
        parsed = urlparse(record["source_url"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append("invalid_source_url")

    if not record.get("name_or_title"):
        errors.append("missing_name_or_title")

    if record.get("price") is not None:
        if not isinstance(record["price"], (int, float)) or record["price"] < 0:
            errors.append("invalid_price")

    if record.get("rating") is not None:
        if not isinstance(record["rating"], (int, float)) or not 0 <= record["rating"] <= 5:
            errors.append("invalid_rating")

    return not errors, errors
