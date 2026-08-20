#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
usage:
  review-branch.sh create <topic> [repository]
  review-branch.sh audit [repository]
  review-branch.sh pre-commit [repository]
  review-branch.sh pre-push
EOF
}

command_name="${1:-}"
if [[ -z "${command_name}" ]]; then
  usage >&2
  exit 2
fi
shift

case "${command_name}" in
  create)
    topic="${1:-}"
    repository="${2:-.}"
    if [[ -z "${topic}" || "${topic}" == -* || ! "${topic}" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
      printf 'invalid topic: use lowercase letters, digits and hyphens\n' >&2
      exit 2
    fi
    if ! git -C "${repository}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      printf 'not a git worktree: %s\n' "${repository}" >&2
      exit 2
    fi
    if [[ -n "$(git -C "${repository}" status --porcelain --untracked-files=all)" ]]; then
      printf 'review snapshot requires a clean worktree\n' >&2
      exit 1
    fi
    head_sha="$(git -C "${repository}" rev-parse --verify HEAD)"
    timestamp="$(date -u '+%Y%m%dT%H%M%SZ')"
    branch="review/${topic}_${timestamp}"
    if git -C "${repository}" show-ref --verify --quiet "refs/heads/${branch}"; then
      printf 'review branch already exists: %s\n' "${branch}" >&2
      exit 1
    fi
    git -C "${repository}" branch "${branch}" "${head_sha}"
    printf 'CREATED review-snapshot: branch=%s sha=%s\n' "${branch}" "${head_sha}"
    ;;

  audit)
    repository="${1:-.}"
    if ! git -C "${repository}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      printf 'not a git worktree: %s\n' "${repository}" >&2
      exit 2
    fi
    findings=0
    while IFS= read -r branch; do
      [[ -z "${branch}" ]] && continue
      if [[ ! "${branch}" =~ ^review/[a-z0-9][a-z0-9-]*_[0-9]{8}T[0-9]{6}Z$ ]]; then
        printf 'R001 invalid local review branch: %s\n' "${branch}"
        findings=$((findings + 1))
      fi
    done < <(git -C "${repository}" for-each-ref --format='%(refname:short)' refs/heads/review/)

    while IFS= read -r branch; do
      [[ -z "${branch}" || "${branch}" != */review/* ]] && continue
      printf 'R002 remote-tracking review branch detected: %s\n' "${branch}"
      findings=$((findings + 1))
    done < <(git -C "${repository}" for-each-ref --format='%(refname:short)' refs/remotes/)

    if (( findings > 0 )); then
      printf 'ATTENTION review-branch: findings=%d\n' "${findings}"
    else
      local_count="$(git -C "${repository}" for-each-ref --count=999999 --format='%(refname)' refs/heads/review/ | wc -l | tr -d ' ')"
      printf 'OK review-branch: local_snapshots=%s remote_tracking=0\n' "${local_count}"
    fi
    ;;

  pre-commit)
    repository="${1:-.}"
    branch="$(git -C "${repository}" symbolic-ref --quiet --short HEAD || true)"
    if [[ "${branch}" == review/* ]]; then
      printf 'blocked commit on immutable local review branch: %s\n' "${branch}" >&2
      exit 1
    fi
    ;;

  pre-push)
    zero_sha='0000000000000000000000000000000000000000'
    blocked=0
    while read -r local_ref local_sha remote_ref remote_sha; do
      [[ -z "${local_ref:-}" ]] && continue
      if [[ "${local_sha}" == "${zero_sha}" ]]; then
        continue
      fi
      if [[ "${local_ref}" == refs/heads/review/* || "${remote_ref}" == refs/heads/review/* ]]; then
        printf 'blocked remote push of local-only review ref: %s -> %s\n' \
          "${local_ref}" "${remote_ref}" >&2
        blocked=1
      fi
    done
    exit "${blocked}"
    ;;

  *)
    usage >&2
    exit 2
    ;;
esac
