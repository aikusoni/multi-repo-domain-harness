#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
usage:
  harness-worktree-guard.sh check [repository]
  harness-worktree-guard.sh audit [repository]
EOF
}

command_name="${1:-}"
if [[ -z "${command_name}" ]]; then
  usage >&2
  exit 2
fi
shift

repository="${1:-.}"
if [[ $# -gt 1 ]]; then
  usage >&2
  exit 2
fi

unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR

if ! inside_worktree="$(git -C "${repository}" rev-parse --is-inside-work-tree 2>/dev/null)" ||
   [[ "${inside_worktree}" != "true" ]]; then
  printf 'ERROR harness-worktree-guard: code=H400 reason=not-a-git-worktree\n' >&2
  exit 2
fi

if ! git_dir="$(git -C "${repository}" rev-parse --path-format=absolute --git-dir 2>/dev/null)" ||
   ! common_dir="$(git -C "${repository}" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"; then
  printf 'ERROR harness-worktree-guard: code=H400 reason=git-metadata-unavailable\n' >&2
  exit 2
fi

if [[ "${git_dir}" == "${common_dir}" ]]; then
  checkout_kind="primary"
else
  checkout_kind="linked"
fi

if ! worktree_count="$(git -C "${repository}" worktree list --porcelain 2>/dev/null | awk '$1 == "worktree" { count += 1 } END { print count + 0 }')"; then
  printf 'ERROR harness-worktree-guard: code=H400 reason=worktree-registry-unavailable\n' >&2
  exit 2
fi

if [[ ! "${worktree_count}" =~ ^[0-9]+$ || "${worktree_count}" -lt 1 ]]; then
  printf 'ERROR harness-worktree-guard: code=H400 reason=invalid-worktree-registry\n' >&2
  exit 2
fi

linked_count=$((worktree_count - 1))

case "${command_name}" in
  check)
    if [[ "${checkout_kind}" == "linked" ]]; then
      printf 'BLOCKED harness-worktree-guard: current=linked mutable_actions=forbidden\n' >&2
      exit 1
    fi

    if [[ "${linked_count}" -gt 0 ]]; then
      printf 'ATTENTION harness-worktree-guard: current=primary linked_registered=%d cleanup_required=true\n' \
        "${linked_count}"
    else
      printf 'OK harness-worktree-guard: current=primary linked_registered=0\n'
    fi
    ;;

  audit)
    findings=0
    if [[ "${checkout_kind}" == "linked" ]]; then
      printf 'H401 current checkout is linked; mutable actions are forbidden\n'
      findings=$((findings + 1))
    fi
    if [[ "${linked_count}" -gt 0 ]]; then
      printf 'H402 registered linked worktrees detected: count=%d\n' "${linked_count}"
      findings=$((findings + 1))
    fi

    if [[ "${findings}" -gt 0 ]]; then
      printf 'ATTENTION harness-worktree-guard: findings=%d current=%s linked_registered=%d\n' \
        "${findings}" "${checkout_kind}" "${linked_count}"
    else
      printf 'OK harness-worktree-guard: findings=0 current=primary linked_registered=0\n'
    fi
    ;;

  *)
    usage >&2
    exit 2
    ;;
esac
