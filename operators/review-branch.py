#!/usr/bin/env python3
"""Create and protect immutable local Git review snapshots."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("topic")
    create.add_argument("repository", nargs="?", default=".")
    create.add_argument("source_ref", nargs="?", default="HEAD")
    for name in ("audit", "pre-commit"):
        command = commands.add_parser(name)
        command.add_argument("repository", nargs="?", default=".")
    # Git supplies remote name and URL as hook arguments. They are not used or logged.
    push = commands.add_parser("pre-push")
    push.add_argument("hook_arguments", nargs="*")
    args = parser.parse_args()

    if args.command == "pre-push":
        blocked = False
        for line in sys.stdin:
            fields = line.split()
            if not fields:
                continue
            if len(fields) != 4:
                print("invalid pre-push input: expected four fields", file=sys.stderr)
                return 2
            local_ref, local_sha, remote_ref, _ = fields
            if local_sha and set(local_sha) == {"0"}:
                continue
            if local_ref.startswith("refs/heads/review/") or remote_ref.startswith("refs/heads/review/"):
                print(f"blocked remote push of local-only review ref: {local_ref} -> {remote_ref}", file=sys.stderr)
                blocked = True
        return int(blocked)

    def git(*arguments: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", args.repository, *arguments], capture_output=True,
            text=True, encoding="utf-8", check=check,
        )

    try:
        if git("rev-parse", "--is-inside-work-tree").stdout.strip() != "true":
            print("not a git worktree", file=sys.stderr)
            return 2
        if args.command == "pre-commit":
            result = git("symbolic-ref", "--quiet", "--short", "HEAD", check=False)
            if result.returncode not in (0, 1):
                raise subprocess.CalledProcessError(result.returncode, result.args)
            branch = result.stdout.strip()
            if branch.startswith("review/"):
                print(f"blocked commit on immutable local review branch: {branch}", file=sys.stderr)
                return 1
            return 0
        if args.command == "create":
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.topic):
                print("invalid topic: use lowercase letters, digits and hyphens", file=sys.stderr)
                return 2
            if args.source_ref == "HEAD" and git("status", "--porcelain", "--untracked-files=all").stdout.strip():
                print("review snapshot requires a clean worktree", file=sys.stderr)
                return 1
            source = git("rev-parse", "--verify", "--end-of-options", f"{args.source_ref}^{{commit}}", check=False)
            if source.returncode:
                print("invalid review source ref", file=sys.stderr)
                return 2
            sha = source.stdout.strip()
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            branch = f"review/{args.topic}_{timestamp}"
            # git branch refuses an existing ref atomically, including concurrent creation.
            created = git("branch", branch, sha, check=False)
            if created.returncode:
                print(f"review branch creation failed or already exists: {branch}", file=sys.stderr)
                return 1
            print(f"CREATED review-snapshot: branch={branch} sha={sha}")
            return 0

        findings = 0
        local = git("for-each-ref", "--format=%(refname:short)", "refs/heads/review/").stdout.splitlines()
        for branch in local:
            if not re.fullmatch(r"review/[a-z0-9][a-z0-9-]*_[0-9]{8}T[0-9]{6}Z", branch):
                print(f"R001 invalid local review branch: {branch}")
                findings += 1
        for branch in git("for-each-ref", "--format=%(refname:short)", "refs/remotes/").stdout.splitlines():
            if "/review/" in branch:
                print(f"R002 remote-tracking review branch detected: {branch}")
                findings += 1
        for line in git("worktree", "list", "--porcelain").stdout.splitlines():
            if line.startswith("branch refs/heads/review/"):
                print(f"R003 review branch attached to worktree: {line.removeprefix('branch refs/heads/')}")
                findings += 1
        if findings:
            print(f"ATTENTION review-branch: findings={findings}")
        else:
            print(f"OK review-branch: local_snapshots={len(local)} remote_tracking=0 attached_review=0")
        return 0
    except (OSError, subprocess.CalledProcessError):
        print("ERROR review-branch: Git command failed; check repository and Git availability", file=sys.stderr)
        return 2


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    raise SystemExit(main())
