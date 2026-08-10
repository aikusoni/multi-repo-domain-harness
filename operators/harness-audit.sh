#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

python3 - "${HARNESS_ROOT}" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path


root = Path(sys.argv[1])


def read(relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def cells(line: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


findings: list[tuple[str, str]] = []
issues = read("ISSUES.md")
active_rows = [
    line
    for line in issues.splitlines()
    if re.match(r"^\| (?:critical|major|minor) \|", line)
]

archived_names = {
    path.name
    for area in ("requests", "proposals")
    for path in (root / area / "archive").glob("*/*.md")
}
active_paths: set[str] = set()

for line in active_rows:
    row = cells(line)
    if len(row) < 3:
        findings.append(("A001", "ISSUES.md: 활성 행을 파싱할 수 없음"))
        continue
    relative = row[2].strip("`")
    expected = 7 if relative.startswith("requests/") else 6 if relative.startswith("proposals/") else None
    if expected is None:
        findings.append(("A002", f"ISSUES.md: 알 수 없는 활성 경로 {relative}"))
        continue
    active_paths.add(relative)
    if len(row) != expected:
        findings.append(("A003", f"ISSUES.md: {relative} 표 열 {len(row)}개, 기대 {expected}개"))
    if not (root / relative).is_file():
        findings.append(("A004", f"ISSUES.md: 활성 파일 없음 {relative}"))
    summary = " | ".join(row[expected - 1 :]) if len(row) >= expected else row[-1]
    utc_stamps = re.findall(r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC\b", summary)
    if len(summary) > 800 or len(utc_stamps) >= 3:
        findings.append(("A005", f"ISSUES.md: 요약 재작성 필요 {relative}"))
    for reference in re.findall(r"(?:requests|proposals)/(?:archive/\d{4}-\d{2}/)?([^`\s|]+\.md)", summary):
        if reference in archived_names:
            findings.append(("A006", f"ISSUES.md: 활성 요약이 아카이브 참조 {relative} -> {reference}"))

targets = [
    "README.md",
    "INDEX.md",
    "ISSUES.md",
    "AGENDA.md",
    "INITIATIVES.md",
    "INVALIDATIONS.md",
    "OPERATORS.md",
    "PROJECTS.md",
    "CURATION.md",
]
targets.extend(str(path.relative_to(root)) for path in sorted((root / "docs").rglob("*.md")))

path_pattern = re.compile(
    r"(?<![\w-])(?:docs|journal|requests|proposals|initiatives|tasks|operators|projects|issues|changed)/"
    r"[A-Za-z0-9._/<>*-]+\.(?:md|json)"
)
placeholder = re.compile(r"YYYY|MM-DD|<[^>]+>|NNN|xxx|\.\.\.|\*", re.IGNORECASE)
for source in targets:
    body = read(source)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    for reference in sorted(set(path_pattern.findall(body))):
        if placeholder.search(reference) or reference in active_paths:
            continue
        if not (root / reference).is_file():
            findings.append(("A101", f"{source}: 로컬 참조 없음 {reference}"))

docs_readme = read("docs/README.md")
registry = docs_readme.split("### 살아있는 문서 등록부", 1)
if len(registry) != 2:
    findings.append(("A201", "docs/README.md: 살아있는 문서 등록부 없음"))
    living_paths: list[str] = []
else:
    registry_body = registry[1].split("\n## ", 1)[0]
    living_paths = sorted(set(re.findall(r"`(docs/[A-Za-z0-9._/-]+\.md)`", registry_body)))

required_headers = (
    ("기준 시각", r"^> \*\*기준 시각:\*\* \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC$"),
    ("그 뒤 미반영분", r"^> \*\*그 뒤 미반영분:\*\* \S.+$"),
    ("현행 정본", r"^> \*\*현행 정본:\*\* \S.+$"),
)
for relative in living_paths:
    path = root / relative
    if not path.is_file():
        findings.append(("A202", f"docs/README.md: 살아있는 문서 없음 {relative}"))
        continue
    head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:24])
    for label, pattern in required_headers:
        if not re.search(pattern, head, re.MULTILINE):
            findings.append(("A203", f"{relative}: 현재성 머리말 누락 {label}"))

if findings:
    print(f"ATTENTION harness-audit: findings={len(findings)}")
    for code, message in findings:
        print(f"{code} {message}")
else:
    print(
        f"OK harness-audit: active_rows={len(active_rows)} "
        f"checked_current_documents={len(targets)} living_documents={len(living_paths)}"
    )
PY
