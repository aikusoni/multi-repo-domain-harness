#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPERATOR="$(cd "${SCRIPT_DIR}/.." && pwd)/review-branch.sh"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "${TEST_ROOT}"' EXIT

REPOSITORY="${TEST_ROOT}/repository"
mkdir -p "${REPOSITORY}"
git -C "${REPOSITORY}" init -q
git -C "${REPOSITORY}" config user.name fixture
git -C "${REPOSITORY}" config user.email fixture@example.invalid
printf 'fixture\n' >"${REPOSITORY}/fixture.txt"
git -C "${REPOSITORY}" add fixture.txt
git -C "${REPOSITORY}" commit -q -m fixture

CREATE_OUTPUT="$("${OPERATOR}" create feedback-loop "${REPOSITORY}")"
[[ "${CREATE_OUTPUT}" == CREATED\ review-snapshot:* ]]
REVIEW_BRANCH="${CREATE_OUTPUT#*branch=}"
REVIEW_BRANCH="${REVIEW_BRANCH%% sha=*}"
HEAD_SHA="$(git -C "${REPOSITORY}" rev-parse HEAD)"
[[ "$(git -C "${REPOSITORY}" rev-parse "${REVIEW_BRANCH}")" == "${HEAD_SHA}" ]]
[[ "$(git -C "${REPOSITORY}" branch --show-current)" != review/* ]]

AUDIT_OUTPUT="$("${OPERATOR}" audit "${REPOSITORY}")"
[[ "${AUDIT_OUTPUT}" == OK\ review-branch:* ]]

printf 'second checkpoint\n' >>"${REPOSITORY}/fixture.txt"
git -C "${REPOSITORY}" add fixture.txt
git -C "${REPOSITORY}" commit -q -m second-checkpoint
EXPLICIT_OUTPUT="$("${OPERATOR}" create prior-checkpoint "${REPOSITORY}" "${HEAD_SHA}")"
EXPLICIT_BRANCH="${EXPLICIT_OUTPUT#*branch=}"
EXPLICIT_BRANCH="${EXPLICIT_BRANCH%% sha=*}"
[[ "$(git -C "${REPOSITORY}" rev-parse "${EXPLICIT_BRANCH}")" == "${HEAD_SHA}" ]]
[[ "$(git -C "${REPOSITORY}" branch --show-current)" != review/* ]]

if "${OPERATOR}" create invalid-source "${REPOSITORY}" refs/heads/missing >/dev/null 2>&1; then
  printf 'expected invalid source ref rejection\n' >&2
  exit 1
fi

printf 'dirty\n' >>"${REPOSITORY}/fixture.txt"
if "${OPERATOR}" create dirty-worktree "${REPOSITORY}" >/dev/null 2>&1; then
  printf 'expected dirty worktree rejection\n' >&2
  exit 1
fi
git -C "${REPOSITORY}" restore fixture.txt

git -C "${REPOSITORY}" branch review/bad-name HEAD
git -C "${REPOSITORY}" update-ref refs/remotes/origin/review/leaked HEAD
REVIEW_WORKTREE="${TEST_ROOT}/review-worktree"
git -C "${REPOSITORY}" worktree add -q "${REVIEW_WORKTREE}" "${REVIEW_BRANCH}"
ATTENTION_OUTPUT="$("${OPERATOR}" audit "${REPOSITORY}")"
[[ "${ATTENTION_OUTPUT}" == *"R001"* ]]
[[ "${ATTENTION_OUTPUT}" == *"R002"* ]]
[[ "${ATTENTION_OUTPUT}" == *"R003"* ]]
[[ "${ATTENTION_OUTPUT}" == *"ATTENTION review-branch"* ]]

if "${OPERATOR}" pre-commit "${REVIEW_WORKTREE}"; then
  printf 'expected commit rejection on attached review branch\n' >&2
  exit 1
fi

ZERO_SHA='0000000000000000000000000000000000000000'
if printf 'refs/heads/review/topic_20260820T000000Z %s refs/heads/review/topic_20260820T000000Z %s\n' \
  "${HEAD_SHA}" "${ZERO_SHA}" | "${OPERATOR}" pre-push; then
  printf 'expected review push rejection\n' >&2
  exit 1
fi
printf 'refs/heads/codex/pr/topic %s refs/heads/codex/pr/topic %s\n' \
  "${HEAD_SHA}" "${ZERO_SHA}" | "${OPERATOR}" pre-push
printf '(delete) %s refs/heads/review/leaked %s\n' \
  "${ZERO_SHA}" "${HEAD_SHA}" | "${OPERATOR}" pre-push

printf 'OK review-branch fixtures\n'
