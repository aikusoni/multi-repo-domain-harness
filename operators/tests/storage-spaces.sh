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
  "${FIXTURE}/indexes"
touch "${FIXTURE}/ISSUES.md" "${FIXTURE}/AGENDA.md" "${FIXTURE}/INITIATIVES.md"
cp "${SOURCE_ROOT}/storage/registry.json" "${FIXTURE}/storage/registry.json"
cp "${SOURCE_ROOT}"/storage/definitions/*.json "${FIXTURE}/storage/definitions/"

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
[[ "${AUDIT_OUTPUT}" == OK\ storage-spaces:*active_spaces=9*catalog_entries=1*transformations=1* ]]

"${OPERATOR}" --root "${FIXTURE}" build-index >/dev/null
cp "${FIXTURE}/indexes/storage-catalog.json" "${TEST_ROOT}/first-index.json"
"${OPERATOR}" --root "${FIXTURE}" build-index >/dev/null
cmp "${TEST_ROOT}/first-index.json" "${FIXTURE}/indexes/storage-catalog.json"

QUERY_OUTPUT="$("${OPERATOR}" --root "${FIXTURE}" query --role record --text relation --limit 5)"
[[ "${QUERY_OUTPUT}" == *'"id": "space:relations"'* ]]
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

ATTENTION_OUTPUT="$("${OPERATOR}" --root "${FIXTURE}" audit)"
[[ "${ATTENTION_OUTPUT}" == ATTENTION\ storage-spaces:* ]]
[[ "${ATTENTION_OUTPUT}" == *"C008"* ]]
[[ "${ATTENTION_OUTPUT}" == *"C009"* ]]
if "${OPERATOR}" --root "${FIXTURE}" build-index >/dev/null 2>&1; then
  printf 'expected invalid storage state to block index build\n' >&2
  exit 1
fi

printf 'OK storage-spaces fixtures\n'
