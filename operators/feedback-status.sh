#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

python3 - "${HARNESS_ROOT}" <<'PY'
from __future__ import annotations

import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path


root = Path(sys.argv[1])
config_path = root / "FEEDBACK.md"
raw_config = config_path.read_text(encoding="utf-8")


def required_config(pattern: str, label: str) -> str:
    match = re.search(pattern, raw_config, re.MULTILINE)
    if not match:
        raise SystemExit(f"invalid FEEDBACK.md: missing or invalid {label}")
    return match.group(1)


window_days = int(
    required_config(r"^- observation_window_days: ([1-9]\d*)$", "observation_window_days")
)
repeat_threshold = int(
    required_config(r"^- repeated_mistake_warning: ([1-9]\d*)$", "repeated_mistake_warning")
)
major_threshold = int(
    required_config(r"^- major_mistake_warning: ([1-9]\d*)$", "major_mistake_warning")
)
required_since_text = required_config(
    r"^- schema_required_since: (\d{4}-\d{2}-\d{2}) UTC$",
    "schema_required_since",
)
required_since = datetime.strptime(required_since_text, "%Y-%m-%d").date()
instruction_ineffective_since = datetime.strptime(
    "2026-09-02 01:38:20 UTC", "%Y-%m-%d %H:%M:%S UTC"
).replace(tzinfo=timezone.utc)

now = datetime.now(timezone.utc)
window_start = now.date() - timedelta(days=window_days - 1)
event_header = re.compile(
    r"^## \[(f-[a-z0-9]{8})\] "
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC) · project: ([A-Za-z0-9._-]+)$",
    re.MULTILINE,
)
field_line = re.compile(r"^- ([a-z_]+): (.+)$", re.MULTILINE)
required_fields = {
    "outcome",
    "category",
    "severity",
    "pattern",
    "introduced_at",
    "detected_at",
    "instruction",
    "task",
    "evidence",
    "supersedes",
    "summary",
}
categories = {
    "success": {
        "instruction-helped",
        "review-caught",
        "validation-passed",
        "safe-promotion",
    },
    "mistake": {
        "instruction-missed",
        "instruction-ambiguous",
        "instruction-missing",
        "instruction-ineffective",
        "execution-error",
        "external-failure",
    },
}
stages = {
    "work",
    "local-review",
    "pull-request",
    "feature",
    "release",
    "canonical",
    "production",
    "not-applicable",
}

findings: list[str] = []
seen_ids: set[str] = set()
events: list[dict[str, str]] = []

feedback_dir = root / "feedback"
for path in sorted(feedback_dir.glob("status-????-??-??.md")):
    try:
        file_date = datetime.strptime(path.name[7:17], "%Y-%m-%d").date()
    except ValueError:
        continue
    if file_date < required_since:
        continue

    body = path.read_text(encoding="utf-8")
    matches = list(event_header.finditer(body))
    valid_headers = {match.group(0) for match in matches}
    for line_number, line in enumerate(body.splitlines(), start=1):
        if line.startswith("## [f-") and line not in valid_headers:
            findings.append(
                f"F012 {path.relative_to(root)}:{line_number} malformed event header"
            )
    for index, match in enumerate(matches):
        event_id, timestamp_text, project = match.groups()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block = body[match.end() : end]
        pairs = field_line.findall(block)
        fields: dict[str, str] = {}
        duplicate_fields: set[str] = set()
        for key, value in pairs:
            if key in fields:
                duplicate_fields.add(key)
            fields[key] = value.strip()

        prefix = f"{path.relative_to(root)}:{event_id}"
        invalid = False
        if event_id in seen_ids:
            findings.append(f"F001 {prefix} duplicate event ID")
            invalid = True
        seen_ids.add(event_id)

        if duplicate_fields:
            findings.append(
                f"F002 {prefix} duplicate fields {','.join(sorted(duplicate_fields))}"
            )
            invalid = True

        missing = sorted(required_fields - fields.keys())
        if missing:
            findings.append(f"F003 {prefix} missing fields {','.join(missing)}")
            invalid = True

        unknown = sorted(fields.keys() - required_fields)
        if unknown:
            findings.append(f"F004 {prefix} unknown fields {','.join(unknown)}")
            invalid = True

        timestamp: datetime | None = None
        try:
            timestamp = datetime.strptime(timestamp_text, "%Y-%m-%d %H:%M:%S UTC").replace(
                tzinfo=timezone.utc
            )
            if timestamp.date() != file_date:
                raise ValueError
        except ValueError:
            findings.append(f"F005 {prefix} timestamp does not match UTC filename date")
            invalid = True

        if missing:
            continue

        outcome = fields["outcome"]
        category = fields["category"]
        severity = fields["severity"]
        if outcome not in categories or category not in categories.get(outcome, set()):
            findings.append(f"F006 {prefix} invalid outcome/category {outcome}/{category}")
            invalid = True
        if (
            category == "instruction-ineffective"
            and timestamp is not None
            and timestamp < instruction_ineffective_since
        ):
            findings.append(f"F014 {prefix} instruction-ineffective predates cutover")
            invalid = True
        if (outcome == "success" and severity != "none") or (
            outcome == "mistake" and severity not in {"minor", "major", "critical"}
        ):
            findings.append(f"F007 {prefix} invalid severity {severity} for {outcome}")
            invalid = True
        if fields["introduced_at"] not in stages or fields["detected_at"] not in stages:
            findings.append(f"F008 {prefix} invalid promotion stage")
            invalid = True
        if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", fields["pattern"]):
            findings.append(f"F009 {prefix} invalid pattern")
            invalid = True
        if not re.fullmatch(r"none|f-[a-z0-9]{8}", fields["supersedes"]):
            findings.append(f"F010 {prefix} invalid supersedes")
            invalid = True
        if (
            not fields["evidence"].strip()
            or fields["evidence"].strip() == "none"
            or "[미검증]" in fields["evidence"]
        ):
            findings.append(f"F011 {prefix} missing evidence")
            invalid = True

        if not invalid and window_start <= file_date <= now.date():
            events.append(
                {
                    "id": event_id,
                    "project": project,
                    **fields,
                }
            )

for event in events:
    supersedes = event["supersedes"]
    if supersedes != "none" and supersedes not in seen_ids:
        findings.append(f"F013 {event['id']} supersedes unknown event {supersedes}")

successes = sum(event["outcome"] == "success" for event in events)
mistakes = sum(event["outcome"] == "mistake" for event in events)
major_mistakes = sum(
    event["outcome"] == "mistake" and event["severity"] in {"major", "critical"}
    for event in events
)
mistake_patterns = Counter(
    event["pattern"] for event in events if event["outcome"] == "mistake"
)
repeated = sorted(
    (pattern, count)
    for pattern, count in mistake_patterns.items()
    if count >= repeat_threshold
)

attention = bool(findings) or major_mistakes >= major_threshold or bool(repeated)
state = "ATTENTION" if attention else "OK"
print(
    f"{state} feedback: window_days={window_days} successes={successes} mistakes={mistakes} "
    f"major_or_critical={major_mistakes}/{major_threshold} "
    f"repeated_patterns={len(repeated)} threshold={repeat_threshold} "
    f"invalid_events={len(findings)}"
)
for pattern, count in repeated:
    print(f"repeat {pattern}={count}")
for finding in findings:
    print(finding)
PY
