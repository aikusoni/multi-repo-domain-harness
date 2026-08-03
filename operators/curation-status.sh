#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

python3 - "${HARNESS_ROOT}" <<'PY'
from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path


root = Path(sys.argv[1])
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
count_threshold = int(required(r"^- root_journal_warning: ([1-9]\d*)$", "root_journal_warning"))
days_threshold = int(required(r"^- stale_after_days: ([1-9]\d*)$", "stale_after_days"))
validity_date_text = required(
    r"^- validity_required_since: (\d{4}-\d{2}-\d{2}) UTC$",
    "validity_required_since",
)

last = datetime.strptime(last_text, "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc)
validity_date = datetime.strptime(validity_date_text, "%Y-%m-%d").date()
now = datetime.now(timezone.utc)
age_days = max(0, (now.date() - last.date()).days)

journal_files = sorted((root / "journal").glob("????-??-??-*.md"))
missing_validity: list[str] = []
for path in journal_files:
    try:
        file_date = datetime.strptime(path.name[:10], "%Y-%m-%d").date()
    except ValueError:
        continue
    if file_date < validity_date:
        continue
    head = path.read_text(encoding="utf-8")[:1200]
    if not re.search(r"^\*\*VALIDITY:\*\* (ACTIVE|SUPERSEDED|REJECTED)$", head, re.MULTILINE):
        missing_validity.append(path.name)

attention = (
    len(journal_files) >= count_threshold
    or age_days >= days_threshold
    or bool(missing_validity)
)
state = "ATTENTION" if attention else "OK"
print(
    f"{state} curation: root_journals={len(journal_files)}/{count_threshold} "
    f"last_curated_at={last_text} age_days={age_days}/{days_threshold} "
    f"missing_validity={len(missing_validity)}"
)
if missing_validity:
    print("missing VALIDITY: " + ", ".join(missing_validity))
PY
