#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPERATOR_SOURCE="$(cd "${SCRIPT_DIR}/.." && pwd)/harness-audit.sh"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "${TEST_ROOT}"' EXIT

make_root() {
  local root="$1"
  mkdir -p "${root}/operators" "${root}/docs"
  cp "${OPERATOR_SOURCE}" "${root}/operators/harness-audit.sh"
  chmod +x "${root}/operators/harness-audit.sh"

  for file in README.md INDEX.md ISSUES.md AGENDA.md INITIATIVES.md INVALIDATIONS.md OPERATORS.md PROJECTS.md CURATION.md FEEDBACK.md; do
    printf '# fixture\n' >"${root}/${file}"
  done
  printf '# docs\n\n### 살아있는 문서 등록부\n' >"${root}/docs/README.md"
  for bootstrap in AGENTS.md CLAUDE.md; do
    cat >"${root}/${bootstrap}" <<'EOF'
# fixture

<!-- harness-bootstrap: read-index-first -->

다른 파일보다 먼저 루트 `INDEX.md` 전체를 읽는다.
EOF
  done
}

VALID_ROOT="${TEST_ROOT}/valid"
make_root "${VALID_ROOT}"
VALID_OUTPUT="$("${VALID_ROOT}/operators/harness-audit.sh")"
[[ "${VALID_OUTPUT}" == OK\ harness-audit:* ]]

MISSING_ROOT="${TEST_ROOT}/missing-marker"
make_root "${MISSING_ROOT}"
printf '# fixture\n\n루트 `INDEX.md` 전체를 먼저 읽는다.\n' >"${MISSING_ROOT}/AGENTS.md"
MISSING_OUTPUT="$("${MISSING_ROOT}/operators/harness-audit.sh")"
[[ "${MISSING_OUTPUT}" == ATTENTION\ harness-audit:* ]]
[[ "${MISSING_OUTPUT}" == *"A301 AGENTS.md"* ]]

NEGATIVE_ROOT="${TEST_ROOT}/negative"
make_root "${NEGATIVE_ROOT}"
cat >"${NEGATIVE_ROOT}/AGENTS.md" <<'EOF'
# fixture

<!-- harness-bootstrap: read-index-first -->

루트 `INDEX.md`를 읽지 않는다.
EOF
NEGATIVE_OUTPUT="$("${NEGATIVE_ROOT}/operators/harness-audit.sh")"
[[ "${NEGATIVE_OUTPUT}" == ATTENTION\ harness-audit:* ]]
[[ "${NEGATIVE_OUTPUT}" == *"A301 AGENTS.md"* ]]

printf 'OK harness-audit fixtures\n'
