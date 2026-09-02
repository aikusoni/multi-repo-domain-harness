#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPERATOR_SOURCE="$(cd "${SCRIPT_DIR}/.." && pwd)/feedback-status.sh"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "${TEST_ROOT}"' EXIT

TODAY="$(date -u '+%Y-%m-%d')"

make_root() {
  local root="$1"
  local required_since="${2:-${TODAY}}"
  mkdir -p "${root}/operators" "${root}/feedback"
  cp "${OPERATOR_SOURCE}" "${root}/operators/feedback-status.sh"
  chmod +x "${root}/operators/feedback-status.sh"
  cat >"${root}/FEEDBACK.md" <<EOF
- observation_window_days: 30
- repeated_mistake_warning: 3
- major_mistake_warning: 1
- schema_required_since: ${required_since} UTC
EOF
}

event() {
  local id="$1"
  local outcome="$2"
  local category="$3"
  local severity="$4"
  local pattern="$5"
  local event_date="${6:-${TODAY}}"
  local event_time="${7:-00:00:00}"
  cat <<EOF
## [${id}] ${event_date} ${event_time} UTC · project: harness
- outcome: ${outcome}
- category: ${category}
- severity: ${severity}
- pattern: ${pattern}
- introduced_at: work
- detected_at: local-review
- instruction: \`docs/example.md\`
- task: none
- evidence: fixture validation
- supersedes: none
- summary: fixture event

EOF
}

EMPTY_ROOT="${TEST_ROOT}/empty"
make_root "${EMPTY_ROOT}"
EMPTY_OUTPUT="$("${EMPTY_ROOT}/operators/feedback-status.sh")"
[[ "${EMPTY_OUTPUT}" == OK\ feedback:*successes=0*mistakes=0* ]]

REPEAT_ROOT="${TEST_ROOT}/repeat"
make_root "${REPEAT_ROOT}"
{
  printf '# fixture\n\n'
  event f-00000001 mistake instruction-missed minor missed-index
  event f-00000002 mistake instruction-missed minor missed-index
  event f-00000003 mistake instruction-missed minor missed-index
} >"${REPEAT_ROOT}/feedback/status-${TODAY}.md"
REPEAT_OUTPUT="$("${REPEAT_ROOT}/operators/feedback-status.sh")"
[[ "${REPEAT_OUTPUT}" == ATTENTION\ feedback:*repeated_patterns=1* ]]
[[ "${REPEAT_OUTPUT}" == *"repeat missed-index=3"* ]]

MAJOR_ROOT="${TEST_ROOT}/major"
make_root "${MAJOR_ROOT}"
{
  printf '# fixture\n\n'
  event f-00000004 mistake instruction-missing major missing-gate
} >"${MAJOR_ROOT}/feedback/status-${TODAY}.md"
MAJOR_OUTPUT="$("${MAJOR_ROOT}/operators/feedback-status.sh")"
[[ "${MAJOR_OUTPUT}" == ATTENTION\ feedback:*major_or_critical=1/1* ]]

INEFFECTIVE_ROOT="${TEST_ROOT}/ineffective"
make_root "${INEFFECTIVE_ROOT}"
{
  printf '# fixture\n\n'
  event f-00000006 mistake instruction-ineffective minor ineffective-rule "${TODAY}" 23:59:59
} >"${INEFFECTIVE_ROOT}/feedback/status-${TODAY}.md"
INEFFECTIVE_OUTPUT="$("${INEFFECTIVE_ROOT}/operators/feedback-status.sh")"
[[ "${INEFFECTIVE_OUTPUT}" == OK\ feedback:*mistakes=1*invalid_events=0* ]]

PRECUTOVER_ROOT="${TEST_ROOT}/ineffective-pre-cutover"
make_root "${PRECUTOVER_ROOT}" 2026-09-02
{
  printf '# fixture\n\n'
  event f-00000007 mistake instruction-ineffective minor ineffective-rule 2026-09-02 01:38:19
} >"${PRECUTOVER_ROOT}/feedback/status-2026-09-02.md"
PRECUTOVER_OUTPUT="$("${PRECUTOVER_ROOT}/operators/feedback-status.sh")"
[[ "${PRECUTOVER_OUTPUT}" == ATTENTION\ feedback:*invalid_events=* ]]
[[ "${PRECUTOVER_OUTPUT}" == *"F014"* ]]

INVALID_ROOT="${TEST_ROOT}/invalid"
make_root "${INVALID_ROOT}"
cat >"${INVALID_ROOT}/feedback/status-${TODAY}.md" <<EOF
# fixture

## [f-00000005] ${TODAY} 00:00:00 UTC · project: harness
- outcome: success
- category: instruction-missed
- severity: major
EOF
INVALID_OUTPUT="$("${INVALID_ROOT}/operators/feedback-status.sh")"
[[ "${INVALID_OUTPUT}" == ATTENTION\ feedback:*invalid_events=* ]]
[[ "${INVALID_OUTPUT}" == *"F003"* ]]

MALFORMED_ROOT="${TEST_ROOT}/malformed"
make_root "${MALFORMED_ROOT}"
cat >"${MALFORMED_ROOT}/feedback/status-${TODAY}.md" <<EOF
# fixture

## [f-broken] ${TODAY} 00:00:00 UTC · project: harness
EOF
MALFORMED_OUTPUT="$("${MALFORMED_ROOT}/operators/feedback-status.sh")"
[[ "${MALFORMED_OUTPUT}" == *"F012"* ]]

printf 'OK feedback-status fixtures\n'
