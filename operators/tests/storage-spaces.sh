#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OPERATOR="${SOURCE_ROOT}/operators/storage-spaces.py"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "${TEST_ROOT}"' EXIT

FIXTURE="${TEST_ROOT}/fixture"
mkdir -p \
  "${FIXTURE}/storage/definitions" \
  "${FIXTURE}/storage/adapters" \
  "${FIXTURE}/storage/catalog" \
  "${FIXTURE}/storage/transformations" \
  "${FIXTURE}/storage/spaces/evidence" \
  "${FIXTURE}/storage/spaces/objects" \
  "${FIXTURE}/storage/spaces/relations" \
  "${FIXTURE}/storage/spaces/residuals" \
  "${FIXTURE}/journal" \
  "${FIXTURE}/requests" \
  "${FIXTURE}/proposals" \
  "${FIXTURE}/issues" \
  "${FIXTURE}/changed" \
  "${FIXTURE}/feedback" \
  "${FIXTURE}/tasks" \
  "${FIXTURE}/indexes" \
  "${FIXTURE}/research"
touch "${FIXTURE}/ISSUES.md" "${FIXTURE}/AGENDA.md" "${FIXTURE}/INITIATIVES.md"
cp "${SOURCE_ROOT}/storage/registry.json" "${FIXTURE}/storage/registry.json"
cp "${SOURCE_ROOT}"/storage/definitions/*.json "${FIXTURE}/storage/definitions/"
cp "${SOURCE_ROOT}/research/catalog.json" "${FIXTURE}/research/catalog.json"

cat >"${FIXTURE}/storage/adapters/registry.json" <<'JSON'
{
  "schema_version": 1,
  "adapters": [
    { "id": "adapter:fixture", "definition": "storage/adapters/fixture.json" }
  ],
  "recorded_at": "2026-08-28 00:00:00 UTC"
}
JSON

cat >"${FIXTURE}/storage/adapters/fixture.json" <<'JSON'
{
  "schema_version": 1,
  "id": "adapter:fixture",
  "type": "embedded",
  "status": "active",
  "implementation": "fixture:adapter-v1",
  "operations": {
    "write": { "support": "supported", "notes": "fixture write" },
    "query": { "support": "supported", "notes": "fixture query" },
    "trace": { "support": "supported", "notes": "fixture trace" },
    "export": { "support": "supported", "notes": "fixture export" },
    "rebuild": { "support": "degraded", "notes": "fixture rebuild" },
    "health": { "support": "supported", "notes": "fixture health" }
  },
  "query_modes": ["exact", "state", "time-range"],
  "input_formats": ["json"],
  "output_formats": ["jsonl"],
  "consistency": "snapshot",
  "license_status": "compatible",
  "public_safety": { "classification": "public-metadata-only", "raw_content_allowed": false },
  "recorded_at": "2026-08-28 00:00:00 UTC"
}
JSON

python3 - "${FIXTURE}/storage/definitions/objects.json" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
definition = json.loads(path.read_text(encoding="utf-8"))
definition["implementation"]["strategy"] = "adapter"
definition["implementation"]["adapter"] = "adapter:fixture"
definition["implementation"]["candidates"] = [
    {
        "id": "candidate:fixture",
        "type": "embedded",
        "status": "selected",
        "research_refs": ["research:bigdawg-polystore"],
        "license_status": "compatible",
        "maintenance_status": "active",
        "notes": "fixture candidate",
    }
]
path.write_text(json.dumps(definition, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

cat >"${FIXTURE}/storage/transformations/event-to-object.json" <<'JSON'
{
  "schema_version": 1,
  "id": "transformation:event-to-object",
  "version": 1,
  "method": "fixture projection",
  "inputs": [
    { "space": "space:harness-events", "ref_pattern": "fixture:issues/*.md" }
  ],
  "outputs": [
    { "space": "space:objects", "ref_pattern": "fixture:objects/*.json" }
  ],
  "preserves": ["identity", "event time"],
  "losses": ["unstructured detail"],
  "reversible": false,
  "implementation": "fixture:manual-v1",
  "recorded_at": "2026-08-28 00:00:00 UTC"
}
JSON

cat >"${FIXTURE}/storage/catalog/observation.json" <<'JSON'
{
  "schema_version": 1,
  "id": "catalog:fixture-observation",
  "type": "fixture-observation",
  "recorded_at": "2026-08-28 00:00:00 UTC",
  "representations": [
    {
      "space": "space:harness-events",
      "ref": "fixture:issues/status.md",
      "role": "record",
      "valid_from": "2026-08-28 00:00:00 UTC"
    },
    {
      "space": "space:objects",
      "ref": "fixture:objects/one.json",
      "role": "record",
      "confidence": 0.8
    }
  ],
  "lineage": {
    "sources": [
      { "space": "space:evidence-references", "ref": "fixture:evidence/run-1" }
    ],
    "transformation": "transformation:event-to-object"
  },
  "public_safety": { "reviewed": true, "classification": "public-metadata-only" }
}
JSON

AUDIT_OUTPUT="$("${OPERATOR}" --root "${FIXTURE}" audit)"
[[ "${AUDIT_OUTPUT}" == OK\ storage-spaces:*active_spaces=9*adapters=1*research_refs=6*catalog_entries=1*transformations=1* ]]

"${OPERATOR}" --root "${FIXTURE}" build-index >/dev/null
cp "${FIXTURE}/indexes/storage-catalog.json" "${TEST_ROOT}/first-index.json"
"${OPERATOR}" --root "${FIXTURE}" build-index >/dev/null
cmp "${TEST_ROOT}/first-index.json" "${FIXTURE}/indexes/storage-catalog.json"

QUERY_OUTPUT="$("${OPERATOR}" --root "${FIXTURE}" query --role record --text relation --limit 5)"
[[ "${QUERY_OUTPUT}" == *'"id": "space:relations"'* ]]
ADAPTER_OUTPUT="$("${OPERATOR}" --root "${FIXTURE}" query --id adapter:fixture --limit 5)"
[[ "${ADAPTER_OUTPUT}" == *'"record_type": "adapter"'* ]]
PLAN_OUTPUT="$("${OPERATOR}" --root "${FIXTURE}" plan --mode relation --mode evidence --limit 5)"
[[ "${PLAN_OUTPUT}" == *'"space": "space:cross-space-catalog"'* ]]
[[ "${PLAN_OUTPUT}" == *'"unserved_modes": []'* ]]
CONTEXT_OUTPUT="$("${OPERATOR}" --root "${FIXTURE}" context catalog:fixture-observation --limit 1)"
[[ "${CONTEXT_OUTPUT}" == *'"omitted_representations": 1'* ]]
[[ "${CONTEXT_OUTPUT}" == *'"id": "transformation:event-to-object"'* ]]

cat >"${FIXTURE}/storage/catalog/unsafe.json" <<'JSON'
{
  "schema_version": 1,
  "id": "catalog:unsafe-fixture",
  "type": "fixture-observation",
  "recorded_at": "2026-08-28 00:00:00 UTC",
  "representations": [
    { "space": "space:unregistered", "ref": "fixture:/private/content" },
    { "space": "space:objects", "ref": "https://example.invalid/private" }
  ],
  "lineage": { "sources": [] },
  "public_safety": { "reviewed": false, "classification": "public-metadata-only" }
}
JSON

python3 - \
  "${FIXTURE}/storage/definitions/objects.json" \
  "${FIXTURE}/storage/adapters/fixture.json" \
  "${FIXTURE}/research/catalog.json" <<'PY'
import json
import sys
from pathlib import Path

object_path, adapter_path, research_path = map(Path, sys.argv[1:])
definition = json.loads(object_path.read_text(encoding="utf-8"))
definition["implementation"]["candidates"][0]["research_refs"].append("research:missing")
object_path.write_text(json.dumps(definition, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
adapter["license_status"] = "not-reviewed"
adapter["query_modes"].remove("time-range")
adapter_path.write_text(json.dumps(adapter, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

catalog = json.loads(research_path.read_text(encoding="utf-8"))
catalog["entries"][0]["source"]["url"] = "http://127.0.0.1/private"
research_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

ATTENTION_OUTPUT="$("${OPERATOR}" --root "${FIXTURE}" audit)"
[[ "${ATTENTION_OUTPUT}" == ATTENTION\ storage-spaces:* ]]
[[ "${ATTENTION_OUTPUT}" == *"C008"* ]]
[[ "${ATTENTION_OUTPUT}" == *"C009"* ]]
[[ "${ATTENTION_OUTPUT}" == *"D111"* ]]
[[ "${ATTENTION_OUTPUT}" == *"R008"* ]]
[[ "${ATTENTION_OUTPUT}" == *"S123"* ]]
[[ "${ATTENTION_OUTPUT}" == *"S143"* ]]
if "${OPERATOR}" --root "${FIXTURE}" build-index >/dev/null 2>&1; then
  printf 'expected invalid storage state to block index build\n' >&2
  exit 1
fi

printf 'OK storage-spaces fixtures\n'
