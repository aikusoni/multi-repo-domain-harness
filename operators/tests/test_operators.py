"""Portable operator contract tests; run with unittest discovery."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class FixtureTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="harness tests ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "공백 fixture"
        self.root.mkdir()

    def write(self, relative, body):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def operator(self, name, *args, code=0, env=None, input=None, cwd=None):
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-8"
        if env:
            environment.update(env)
        result = subprocess.run(
            [sys.executable, str(ROOT / "operators" / f"{name}.py"), *map(str, args)],
            input=input, capture_output=True, encoding="utf-8", env=environment,
            cwd=cwd or self.root,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def git(self, *args, repository=None):
        environment = os.environ.copy()
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
            environment.pop(name, None)
        result = subprocess.run(
            ["git", "-C", str(repository or self.root), *map(str, args)],
            capture_output=True, encoding="utf-8", env=environment,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def init_git(self):
        self.git("init", "-q")
        self.git("config", "user.name", "fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.write("fixture.txt", "fixture\n")
        self.git("add", "fixture.txt")
        self.git("commit", "-q", "-m", "fixture")


class GuardTests(FixtureTest):
    def test_primary_linked_pollution_and_read_only(self):
        self.init_git()
        expected = "OK harness-worktree-guard: current=primary linked_registered=0\n"
        self.assertEqual(self.operator("harness-worktree-guard", "check", self.root), expected)
        nested = self.root / "nested/path"
        nested.mkdir(parents=True)
        self.assertEqual(self.operator("harness-worktree-guard", "check", nested), expected)
        invalid = self.root.parent / "not git"
        invalid.mkdir()
        for target in (invalid, self.root / ".git"):
            self.assertEqual(self.operator("harness-worktree-guard", "check", target, code=2),
                             "ERROR harness-worktree-guard: code=H400 reason=not-a-git-worktree\n")
        linked = self.root.parent / "linked 공백"
        self.git("worktree", "add", "-q", "-b", "fixture-linked", linked)
        polluted = {"GIT_DIR": str(self.root / ".git"), "GIT_COMMON_DIR": str(self.root / ".git"), "GIT_WORK_TREE": str(self.root)}
        outputs = []
        for env in ({}, polluted):
            output = self.operator("harness-worktree-guard", "check", linked, code=1, env=env)
            self.assertEqual(output, "BLOCKED harness-worktree-guard: current=linked mutable_actions=forbidden\n")
            outputs.append(output)
        (linked / "fixture.txt").write_text("dirty\n", encoding="utf-8")
        before = self.git("status", "--porcelain", repository=linked)
        output = self.operator("harness-worktree-guard", "audit", linked)
        self.assertIn("H401", output)
        self.assertIn("H402", output)
        self.assertIn("findings=2 current=linked linked_registered=1", output)
        self.assertEqual(before, self.git("status", "--porcelain", repository=linked))
        outputs.append(output)
        output = self.operator("harness-worktree-guard", "check", self.root)
        self.assertIn("ATTENTION", output)
        self.assertIn("cleanup_required=true", output)
        outputs.append(output)
        output = self.operator("harness-worktree-guard", "audit", self.root)
        self.assertIn("findings=1 current=primary linked_registered=1", output)
        outputs.append(output)
        for output in outputs:
            self.assertNotIn(str(self.root.parent), output)
        self.git("restore", "fixture.txt", repository=linked)
        self.git("worktree", "remove", linked)
        self.assertEqual(self.operator("harness-worktree-guard", "audit", self.root),
                         "OK harness-worktree-guard: findings=0 current=primary linked_registered=0\n")

    def test_git_missing_and_bad_arguments(self):
        output = self.operator("harness-worktree-guard", "check", self.root, env={"PATH": ""}, code=2)
        self.assertIn("H400", output)
        self.operator("harness-worktree-guard", "unknown", code=2)
        self.operator("harness-worktree-guard", "check", self.root, "extra", code=2)


class ReviewTests(FixtureTest):
    def test_snapshots_audit_and_hooks(self):
        self.init_git()
        sha = self.git("rev-parse", "HEAD")
        output = self.operator("review-branch", "create", "feedback-loop", self.root)
        branch = re.search(r"branch=(\S+) sha=", output).group(1)
        self.assertRegex(branch, r"^review/feedback-loop_\d{8}T\d{6}Z$")
        self.assertEqual(self.git("rev-parse", branch), sha)
        self.assertFalse(self.git("branch", "--show-current").startswith("review/"))
        self.assertIn("OK review-branch:", self.operator("review-branch", "audit", self.root))
        self.write("fixture.txt", "second checkpoint\n")
        self.git("add", "fixture.txt")
        self.git("commit", "-q", "-m", "second")
        self.write("fixture.txt", "dirty\n")
        explicit = self.operator("review-branch", "create", "prior-checkpoint", self.root, sha)
        prior = re.search(r"branch=(\S+) sha=", explicit).group(1)
        self.assertEqual(self.git("rev-parse", prior), sha)
        self.operator("review-branch", "create", "dirty-worktree", self.root, code=1)
        self.operator("review-branch", "create", "invalid-source", self.root, "missing", code=2)
        self.operator("review-branch", "create", "BAD", self.root, code=2)
        self.git("restore", "fixture.txt")
        self.git("branch", "review/bad-name", "HEAD")
        self.git("update-ref", "refs/remotes/origin/review/leaked", "HEAD")
        linked = self.root.parent / "review worktree"
        self.git("worktree", "add", "-q", linked, branch)
        output = self.operator("review-branch", "audit", self.root)
        for code in ("R001", "R002", "R003", "ATTENTION"):
            self.assertIn(code, output)
        self.operator("review-branch", "pre-commit", linked, code=1)
        self.operator("review-branch", "pre-commit", self.root)
        self.git("checkout", "--detach", "-q", repository=linked)
        self.operator("review-branch", "pre-commit", linked)
        self.operator("review-branch", "pre-commit", self.root.parent, code=2)
        zero = "0" * 40
        for local, remote in ((branch, branch), ("codex/work", branch), (branch, "codex/work")):
            self.operator("review-branch", "pre-push", input=f"refs/heads/{local} {sha} refs/heads/{remote} {zero}\n", code=1)
        self.operator("review-branch", "pre-push", "origin", "unused", input=f"refs/heads/codex/work {sha} refs/heads/codex/work {zero}\n")
        self.operator("review-branch", "pre-push", input=f"(delete) {zero} refs/heads/review/leaked {sha}\n")
        self.operator("review-branch", "pre-push", input="malformed\n", code=2)
        self.operator("review-branch", "pre-push", input="")
        self.git("worktree", "remove", linked)


class AuditTests(FixtureTest):
    def setUp(self):
        super().setUp()
        for name in ("README", "INDEX", "ISSUES", "AGENDA", "INITIATIVES", "INVALIDATIONS", "OPERATORS", "PROJECTS", "CURATION", "FEEDBACK"):
            self.write(name + ".md", "# fixture\n")
        self.write("docs/README.md", "# docs\n\n### 살아있는 문서 등록부\n")
        self.bootstrap = "<!-- harness-bootstrap: read-index-first -->\n다른 파일보다 먼저 루트 `INDEX.md` 전체를 읽는다.\n"
        for name in ("AGENTS", "CLAUDE"):
            self.write(name + ".md", self.bootstrap)

    def test_bootstrap_and_document_findings(self):
        self.assertIn("OK harness-audit:", self.operator("harness-audit", "--root", self.root))
        for body in ("루트 `INDEX.md` 전체를 먼저 읽는다.\n", "<!-- harness-bootstrap: read-index-first -->\n루트 `INDEX.md`를 읽지 않는다.\n"):
            self.write("AGENTS.md", body)
            self.assertIn("A301 AGENTS.md", self.operator("harness-audit", "--root", self.root))
        self.write("AGENTS.md", self.bootstrap)
        self.write("requests/archive/2026-09/old.md", "# archived\n")
        self.write("ISSUES.md", "| major | open | `requests/missing.md` | harness | harness | - | " + "x" * 801 + " requests/archive/2026-09/old.md |\n")
        self.write("README.md", "docs/missing.md\n")
        self.write("docs/README.md", "### 살아있는 문서 등록부\n`docs/living.md`\n")
        self.write("docs/living.md", "# missing headers\n")
        output = self.operator("harness-audit", "--root", self.root)
        for code in ("A004", "A005", "A006", "A101", "A203"):
            self.assertIn(code, output)

    def test_missing_input_fails(self):
        (self.root / "INDEX.md").unlink()
        self.operator("harness-audit", "--root", self.root, code=1)


class FeedbackTests(FixtureTest):
    def setUp(self):
        super().setUp()
        self.today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.config()

    def config(self, since=None):
        self.write("FEEDBACK.md", f"- observation_window_days: 30\n- repeated_mistake_warning: 3\n- major_mistake_warning: 1\n- schema_required_since: {since or self.today} UTC\n")

    def event(self, id="f-00000001", outcome="mistake", category="instruction-missed", severity="minor", pattern="missed-index", date=None, time="00:00:00"):
        return f"""## [{id}] {date or self.today} {time} UTC · project: harness
- outcome: {outcome}
- category: {category}
- severity: {severity}
- pattern: {pattern}
- introduced_at: work
- detected_at: local-review
- instruction: `docs/example.md`
- task: none
- evidence: fixture validation
- supersedes: none
- summary: fixture event

"""

    def status(self, body, date=None):
        self.write(f"feedback/status-{date or self.today}.md", body)
        return self.operator("feedback-status", "--root", self.root)

    def test_empty_repeat_major_and_cutover(self):
        output = self.operator("feedback-status", "--root", self.root)
        self.assertIn("OK feedback:", output)
        self.assertIn("successes=0 mistakes=0", output)
        output = self.status("".join(self.event(id=f"f-{n:08d}") for n in range(1, 4)))
        self.assertIn("repeated_patterns=1", output)
        self.assertIn("repeat missed-index=3", output)
        self.assertIn("major_or_critical=1/1", self.status(self.event(severity="major", category="instruction-missing")))
        output = self.status(self.event(category="instruction-ineffective", time="23:59:59"))
        self.assertIn("mistakes=1", output)
        self.assertIn("invalid_events=0", output)
        self.config("2026-09-02")
        output = self.status(self.event(date="2026-09-02", time="01:38:19", category="instruction-ineffective"), date="2026-09-02")
        self.assertIn("F014", output)

    def test_invalid_events(self):
        self.assertIn("F003", self.status(f"## [f-00000005] {self.today} 00:00:00 UTC · project: harness\n- outcome: success\n"))
        self.assertIn("F012", self.status(f"## [f-broken] {self.today} 00:00:00 UTC · project: harness\n"))
        output = self.status(self.event(outcome="success", severity="major"))
        self.assertIn("F006", output)
        self.assertIn("F007", output)
        output = self.status(self.event() + self.event())
        self.assertIn("F001", output)
        output = self.status(self.event() + "- outcome: mistake\n- unknown: value\n")
        self.assertIn("F002", output)
        self.assertIn("F004", output)
        self.write("FEEDBACK.md", "invalid\n")
        self.operator("feedback-status", "--root", self.root, code=1)

    def test_timezone_and_cwd_independent(self):
        self.status(self.event())
        outputs = [self.operator("feedback-status", "--root", self.root, env={"TZ": zone}) for zone in ("Asia/Seoul", "America/Los_Angeles", "UTC")]
        self.assertEqual(len(set(outputs)), 1)


class CurationTests(FixtureTest):
    def test_root_archive_validity_and_timezone(self):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.write("CURATION.md", f"- last_curated_at: {today} 00:00:00 UTC\n- uncurated_journal_warning: 2\n- stale_after_days: 14\n- validity_required_since: {today} UTC\n")
        self.assertIn("OK curation:", self.operator("curation-status", "--root", self.root))
        self.write(f"journal/{today}-new.md", "**VALIDITY:** ACTIVE\n" + today + " 23:59:59 UTC\n")
        self.write(f"journal/archive/{today[:7]}/{today}-archive.md", "# missing validity\n")
        outputs = [self.operator("curation-status", "--root", self.root, env={"TZ": zone}) for zone in ("Asia/Seoul", "America/Los_Angeles", "UTC")]
        self.assertEqual(len(set(outputs)), 1)
        self.assertIn("ATTENTION curation:", outputs[0])
        self.assertIn("uncurated_journals=2/2 archived_uncurated=1", outputs[0])
        self.assertIn("age_days=0/14 missing_validity=1", outputs[0])
        self.write("CURATION.md", "invalid\n")
        self.operator("curation-status", "--root", self.root, code=1)

    def test_default_root_follows_script(self):
        self.write("CURATION.md", "- last_curated_at: 2020-01-01 00:00:00 UTC\n- uncurated_journal_warning: 2\n- stale_after_days: 14\n- validity_required_since: 2020-01-01 UTC\n")
        target = self.root / "operators/curation-status.py"
        target.parent.mkdir()
        shutil.copyfile(ROOT / "operators/curation-status.py", target)
        result = subprocess.run([sys.executable, str(target)], cwd=self.root.parent, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ATTENTION curation:", result.stdout)


if __name__ == "__main__":
    unittest.main()
