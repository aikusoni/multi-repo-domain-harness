#!/usr/bin/env python3
"""Check the harness primary checkout without exposing repository paths."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "audit"))
    parser.add_argument("repository", nargs="?", default=".")
    args = parser.parse_args()
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)

    def git(*arguments: str) -> str:
        result = subprocess.run(
            ["git", "-C", args.repository, *arguments], env=env,
            capture_output=True, text=True, encoding="utf-8", check=True,
        )
        return result.stdout.strip()

    reason = "not-a-git-worktree"
    try:
        if git("rev-parse", "--is-inside-work-tree") != "true":
            raise ValueError
        reason = "git-metadata-unavailable"
        git_dir = git("rev-parse", "--path-format=absolute", "--git-dir")
        common_dir = git("rev-parse", "--path-format=absolute", "--git-common-dir")
        if not git_dir or not common_dir:
            raise ValueError
        kind = "primary" if Path(git_dir).resolve() == Path(common_dir).resolve() else "linked"
        reason = "worktree-registry-unavailable"
        registry = git("worktree", "list", "--porcelain")
        count = sum(line.startswith("worktree ") for line in registry.splitlines())
        reason = "invalid-worktree-registry"
        if count < 1:
            raise ValueError
    except (OSError, subprocess.CalledProcessError, ValueError):
        print(f"ERROR harness-worktree-guard: code=H400 reason={reason}", file=sys.stderr)
        return 2

    linked = count - 1
    if args.command == "check":
        if kind == "linked":
            print("BLOCKED harness-worktree-guard: current=linked mutable_actions=forbidden", file=sys.stderr)
            return 1
        if linked:
            print(f"ATTENTION harness-worktree-guard: current=primary linked_registered={linked} cleanup_required=true")
        else:
            print("OK harness-worktree-guard: current=primary linked_registered=0")
        return 0

    findings = int(kind == "linked") + int(linked > 0)
    if kind == "linked":
        print("H401 current checkout is linked; mutable actions are forbidden")
    if linked:
        print(f"H402 registered linked worktrees detected: count={linked}")
    if findings:
        print(f"ATTENTION harness-worktree-guard: findings={findings} current={kind} linked_registered={linked}")
    else:
        print("OK harness-worktree-guard: findings=0 current=primary linked_registered=0")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
