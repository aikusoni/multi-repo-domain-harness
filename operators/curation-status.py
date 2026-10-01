#!/usr/bin/env python3
"""curation-status harness operator (Python standard library)."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(root: Path) -> int:
    config_path = root / "CURATION.md"
    raw = config_path.read_text(encoding="utf-8")

    def required(pattern: str, label: str) -> str:
        match = re.search(pattern, raw, re.MULTILINE)
        if not match:
            raise SystemExit(f"invalid CURATION.md: missing or invalid {label}")
        return match.group(1)

    last_text = required(
        r"^- last_curated_at: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC)$",
        "last_curated_at",
    )
    count_threshold = int(
        required(r"^- uncurated_journal_warning: ([1-9]\d*)$", "uncurated_journal_warning")
    )
    days_threshold = int(required(r"^- stale_after_days: ([1-9]\d*)$", "stale_after_days"))
    validity_date_text = required(
        r"^- validity_required_since: (\d{4}-\d{2}-\d{2}) UTC$",
        "validity_required_since",
    )

    last = datetime.strptime(last_text, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
    validity_date = datetime.strptime(validity_date_text, "%Y-%m-%d").date()
    now = datetime.now(timezone.utc)
    age_days = max(0, (now.date() - last.date()).days)

    journal_files = sorted(
        list((root / "journal").glob("????-??-??-*.md"))
        + list((root / "journal" / "archive").glob("????-??/????-??-??-*.md"))
    )
    uncurated: list[Path] = []
    missing_validity: list[str] = []
    for path in journal_files:
        try:
            file_date = datetime.strptime(path.name[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        body = path.read_text(encoding="utf-8")
        timestamps = [
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
            for value in re.findall(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC\b", body)
        ]
        activity_at = max(timestamps) if timestamps else datetime.combine(
            file_date,
            datetime.max.time(),
            tzinfo=timezone.utc,
        )
        if activity_at > last:
            uncurated.append(path)
        if file_date >= validity_date and not re.search(
            r"^\*\*VALIDITY:\*\* (ACTIVE|SUPERSEDED|REJECTED)$",
            body[:1200],
            re.MULTILINE,
        ):
            missing_validity.append(path.name)

    archived_uncurated = sum("archive" in path.parts for path in uncurated)
    attention = (
        len(uncurated) >= count_threshold
        or age_days >= days_threshold
        or bool(missing_validity)
    )
    state = "ATTENTION" if attention else "OK"
    print(
        f"{state} curation: uncurated_journals={len(uncurated)}/{count_threshold} "
        f"archived_uncurated={archived_uncurated} "
        f"last_curated_at={last_text} age_days={age_days}/{days_threshold} "
        f"missing_validity={len(missing_validity)}"
    )
    if missing_validity:
        print("missing VALIDITY: " + ", ".join(missing_validity))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        return run(args.root)
    except (OSError, ValueError) as exc:
        print(f"ERROR curation-status: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
