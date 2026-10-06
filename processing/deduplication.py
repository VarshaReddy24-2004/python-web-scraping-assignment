from __future__ import annotations

import hashlib


def duplicate_key(record: dict) -> str:
    """Build a stable key after text normalization.

    Source URL is the strongest identity when available. The normalized
    source + title + author combination is used as a fallback so that
    harmless whitespace/case differences do not create separate records.
    """
    source_url = (record.get("source_url") or "").strip().casefold()
    if source_url:
        raw = f"url|{source_url}"
    else:
        source = (record.get("source") or "").strip().casefold()
        title = (record.get("name_or_title") or "").strip().casefold()
        author = (record.get("author") or "").strip().casefold()
        raw = f"fallback|{source}|{title}|{author}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def deduplicate(records: list[dict]) -> tuple[list[dict], int]:
    unique: list[dict] = []
    seen: set[str] = set()
    duplicate_count = 0

    for record in records:
        key = duplicate_key(record)
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)
        unique.append(record)

    return unique, duplicate_count
