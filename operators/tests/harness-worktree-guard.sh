#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPERATOR="$(cd "${SCRIPT_DIR}/.." && pwd)/harness-worktree-guard.sh"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "${TEST_ROOT}"' EXIT

REPOSITORY="${TEST_ROOT}/repository"
LINKED="${TEST_ROOT}/linked"
NOT_GIT="${TEST_ROOT}/not-git"
mkdir -p "${REPOSITORY}"
mkdir -p "${NOT_GIT}"
git -C "${REPOSITORY}" init -q
git -C "${REPOSITORY}" config user.name fixture
git -C "${REPOSITORY}" config user.email fixture@example.invalid
printf 'fixture\n' >"${REPOSITORY}/fixture.txt"
git -C "${REPOSITORY}" add fixture.txt
git -C "${REPOSITORY}" commit -q -m fixture

PRIMARY_OUTPUT="$("${OPERATOR}" check "${REPOSITORY}")"
[[ "${PRIMARY_OUTPUT}" == 'OK harness-worktree-guard: current=primary linked_registered=0' ]]

mkdir -p "${REPOSITORY}/nested/path"
NESTED_OUTPUT="$("${OPERATOR}" check "${REPOSITORY}/nested/path")"
[[ "${NESTED_OUTPUT}" == 'OK harness-worktree-guard: current=primary linked_registered=0' ]]

for invalid_path in "${NOT_GIT}" "${REPOSITORY}/.git"; do
  set +e
  INVALID_OUTPUT="$("${OPERATOR}" check "${invalid_path}" 2>&1)"
  INVALID_EXIT=$?
  set -e
  [[ "${INVALID_EXIT}" -eq 2 ]]
  [[ "${INVALID_OUTPUT}" == 'ERROR harness-worktree-guard: code=H400 reason=not-a-git-worktree' ]]
done

git -C "${REPOSITORY}" worktree add -q -b fixture-linked "${LINKED}"

set +e
LINKED_OUTPUT="$("${OPERATOR}" check "${LINKED}" 2>&1)"
LINKED_EXIT=$?
set -e
[[ "${LINKED_EXIT}" -eq 1 ]]
[[ "${LINKED_OUTPUT}" == 'BLOCKED harness-worktree-guard: current=linked mutable_actions=forbidden' ]]

set +e
POLLUTED_OUTPUT="$(GIT_DIR="${REPOSITORY}/.git" GIT_WORK_TREE="${REPOSITORY}" \
  GIT_COMMON_DIR="${REPOSITORY}/.git" "${OPERATOR}" check "${LINKED}" 2>&1)"
POLLUTED_EXIT=$?
set -e
[[ "${POLLUTED_EXIT}" -eq 1 ]]
[[ "${POLLUTED_OUTPUT}" == 'BLOCKED harness-worktree-guard: current=linked mutable_actions=forbidden' ]]

printf 'dirty fixture\n' >>"${LINKED}/fixture.txt"
DIRTY_BEFORE="$(git -C "${LINKED}" status --porcelain --untracked-files=all)"

LINKED_AUDIT="$("${OPERATOR}" audit "${LINKED}")"
[[ "${LINKED_AUDIT}" == *'H401 current checkout is linked; mutable actions are forbidden'* ]]
[[ "${LINKED_AUDIT}" == *'H402 registered linked worktrees detected: count=1'* ]]
[[ "${LINKED_AUDIT}" == *'ATTENTION harness-worktree-guard: findings=2 current=linked linked_registered=1'* ]]
DIRTY_AFTER="$(git -C "${LINKED}" status --porcelain --untracked-files=all)"
[[ "${DIRTY_AFTER}" == "${DIRTY_BEFORE}" ]]

PRIMARY_ATTENTION="$("${OPERATOR}" check "${REPOSITORY}")"
[[ "${PRIMARY_ATTENTION}" == 'ATTENTION harness-worktree-guard: current=primary linked_registered=1 cleanup_required=true' ]]

AUDIT_ATTENTION="$("${OPERATOR}" audit "${REPOSITORY}")"
[[ "${AUDIT_ATTENTION}" == *'H402 registered linked worktrees detected: count=1'* ]]
[[ "${AUDIT_ATTENTION}" == *'ATTENTION harness-worktree-guard: findings=1 current=primary linked_registered=1'* ]]

for output in "${LINKED_OUTPUT}" "${POLLUTED_OUTPUT}" "${LINKED_AUDIT}" \
  "${PRIMARY_ATTENTION}" "${AUDIT_ATTENTION}"; do
  if [[ "${output}" == *"${TEST_ROOT}"* || "${output}" == *"${REPOSITORY}"* || "${output}" == *"${LINKED}"* ]]; then
    printf 'operator output exposed an absolute fixture path\n' >&2
    exit 1
  fi
done

git -C "${LINKED}" restore fixture.txt
git -C "${REPOSITORY}" worktree remove "${LINKED}"
AUDIT_OK="$("${OPERATOR}" audit "${REPOSITORY}")"
[[ "${AUDIT_OK}" == 'OK harness-worktree-guard: findings=0 current=primary linked_registered=0' ]]

printf 'OK harness-worktree-guard fixtures\n'
