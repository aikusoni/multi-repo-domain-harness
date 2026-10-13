"""Claude and Codex CLI adapters. Invoked by the room server, or with --check."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

LINE_LIMIT = 2_000_000


def command(provider, mode="read-only", cli=None, model=None, effort=None):
    binary = cli or provider
    if provider == "codex":
        argv = [binary, "--ask-for-approval", "never", "exec", "--sandbox", mode, "--json"]
        if model:
            argv.extend(["--model", model])
        if effort:
            argv.extend(["--config", "model_reasoning_effort=" + json.dumps(effort)])
        return argv + ["-"]
    if provider == "claude":
        tools = "Read,Glob,Grep" + (",Edit,Write" if mode == "workspace-write" else "")
        argv = [binary, "--print", "--output-format", "json", "--restricted",
                "--permission-mode", "acceptEdits" if mode == "workspace-write" else "dontAsk",
                "--permission-prompts", "none", "--tools", tools, "--allowedTools", tools,
                "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                "--disable-slash-commands", "--no-chrome"]
        if model:
            argv.extend(["--model", model])
        if effort:
            argv.extend(["--effort", effort])
        return argv
    raise ValueError("지원하지 않는 provider")


def preflight(provider, cli=None):
    binary = cli or provider
    if not (Path(binary).is_file() if Path(binary).is_absolute() else shutil.which(binary)):
        raise ValueError(f"{provider} CLI를 찾을 수 없습니다. 설치 후 로컬 cli 경로를 지정하세요.")
    flags = ["exec", "--help"] if provider == "codex" else ["--help"]
    try:
        result = subprocess.run([binary, *flags], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError(f"{provider} CLI를 실행할 수 없습니다. 로컬 설치를 확인하세요.") from None
    required = ("--json", "--sandbox") if provider == "codex" else (
        "--restricted", "--permission-prompts", "--tools", "--output-format")
    if result.returncode or any(flag not in result.stdout for flag in required):
        raise ValueError(f"{provider} CLI가 필요한 옵션을 지원하지 않거나 실행 파일이 손상되었습니다.")


def parse_event(provider, event):
    """Return final text, a failure flag, and whether a final result was observed."""
    if not isinstance(event, dict):
        return "", False, False
    if provider == "codex":
        kind = event.get("type")
        if kind == "item.completed" and event.get("item", {}).get("type") == "agent_message":
            return str(event["item"].get("text", "")), False, True
        if kind in ("turn.failed", "error"):
            return "", True, False
    elif event.get("type") == "result":
        return str(event.get("result", "")), bool(event.get("is_error")), True
    return "", False, False


def run(provider, argv, prompt):
    process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=sys.stderr)
    try:
        # The server limits prompt size; the CLI starts reading stdin immediately.
        process.stdin.write(prompt.encode("utf-8"))
        process.stdin.close()
        final, failed, seen = "", False, False
        for line in iter(lambda: process.stdout.readline(LINE_LIMIT + 1), b""):
            if len(line) > LINE_LIMIT:
                failed = True
                process.kill()
                break
            try:
                events = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                failed = True
                continue
            if not isinstance(events, list):
                events = [events]
            for event in events:
                value, event_failed, observed = parse_event(provider, event)
                failed = failed or event_failed
                seen = seen or observed
                if value:
                    final = value
        code = process.wait()
        if final:
            print(final)
        if code or failed or not seen:
            print(f"{provider} 실행 실패 또는 최종 결과 누락. 부분 변경을 확인하세요.", file=sys.stderr)
            return code if code > 0 else 1
        return 0
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdout.close()
        if not process.stdin.closed:
            process.stdin.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=("codex", "claude"))
    parser.add_argument("--mode", default="read-only", choices=("read-only", "workspace-write"))
    parser.add_argument("--cli", help="owner-configured CLI executable")
    parser.add_argument("--model")
    parser.add_argument("--effort")
    parser.add_argument("--check", action="store_true", help="CLI option probe only; no model call")
    args = parser.parse_args()
    try:
        preflight(args.provider, args.cli)
        if args.check:
            print(f"OK {args.provider}: required CLI options available; authentication not checked")
            return 0
        prompt = sys.stdin.read(500000)
        if not prompt.strip():
            raise ValueError("작업 프롬프트가 없습니다.")
        return run(args.provider, command(args.provider, args.mode, args.cli, args.model, args.effort), prompt)
    except (ValueError, OSError) as error:
        print(str(error) if isinstance(error, ValueError) else "CLI 실행 실패. 로컬 설치를 확인하세요.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
