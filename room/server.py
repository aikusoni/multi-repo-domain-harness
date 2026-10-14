"""Local room server. Python 3.10+, no third-party packages or model defaults."""

import argparse
import copy
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import signal
import socketserver
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

if __package__:
    from .drivers import command as cli_command
else:
    from drivers import command as cli_command

ROOT = Path(__file__).resolve().parent.parent
WEB = Path(__file__).resolve().parent / "web"
ASSETS = {"/": ("index.html", "text/html; charset=utf-8"),
          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
          "/style.css": ("style.css", "text/css; charset=utf-8"),
          "/board": ("board.html", "text/html; charset=utf-8"),
          "/board.js": ("board.js", "text/javascript; charset=utf-8"),
          "/board.css": ("board.css", "text/css; charset=utf-8")}
MAX_TEXT = 24000
MAX_OUTPUT = 64000


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def identifier(prefix):
    return prefix + secrets.token_hex(8)


def transaction():
    return "tx:room-" + secrets.token_hex(4) + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def text(value, limit=MAX_TEXT):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"비어 있지 않은 문자열이 필요합니다 (최대 {limit}자).")
    return value.strip()


def primary(root):
    """Do not let the server launch against a linked harness checkout."""
    paths = []
    for flag in ("--git-dir", "--git-common-dir"):
        p = subprocess.run(["git", "-C", str(root), "rev-parse", flag],
                           capture_output=True, text=True, check=True)
        paths.append((root / p.stdout.strip()).resolve())
    if paths[0] != paths[1]:
        raise ValueError("하네스 서버는 primary checkout에서만 실행할 수 있습니다.")


def load_config(path, root):
    """Only local owner-authored configuration may define commands and paths."""
    root = Path(root).resolve()
    config = json.loads(path.read_text()) if path else {}
    projects = config.get("projects", {})
    drivers = config.get("drivers", {})
    for key, value in projects.items():
        if not re.fullmatch(r"[a-zA-Z0-9._-]+", key):
            raise ValueError("잘못된 project-id")
        location = Path(value).expanduser().resolve()
        if not location.is_dir() or location == root or root in location.parents or location in root.parents:
            raise ValueError("실행 프로젝트는 하네스 밖의 기존 디렉터리여야 합니다.")
        projects[key] = str(location)
    for name, driver in drivers.items():
        text(name, 80)
        provider = driver.get("type", "command")
        if provider in ("claude", "codex"):
            mode = driver.get("mode", "read-only")
            if mode not in ("read-only", "workspace-write"):
                raise ValueError("mode는 read-only 또는 workspace-write입니다.")
            driver["mode"] = mode
            argv = [sys.executable, "-B", str(ROOT / "room" / "drivers.py"), "--provider", provider, "--mode", mode]
            for option in ("cli", "model", "effort"):
                if driver.get(option):
                    argv.extend(["--" + option, text(driver[option], 200)])
            driver["argv"] = argv
        elif provider != "command":
            raise ValueError("type은 command, claude 또는 codex입니다.")
        argv = driver.get("argv")
        if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or not a for a in argv):
            raise ValueError("driver.argv는 비어 있지 않은 문자열 배열이어야 합니다.")
        driver["timeout"] = int(driver.get("timeout", 120))
        if not 1 <= driver["timeout"] <= 3600:
            raise ValueError("driver.timeout은 1~3600초입니다.")
    return {"projects": projects, "drivers": drivers}


class Store:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.directory / "state.json"
        self.lock = threading.RLock()
        self.state = json.loads(self.path.read_text()) if self.path.exists() else {"version": 1, "rooms": {}}
        if self.state.get("version") != 1:
            raise ValueError("지원하지 않는 룸 상태 버전입니다.")
        # Running commands cannot safely be replayed after a crash.
        for room in self.state["rooms"].values():
            for job in room["jobs"].values():
                if job["status"] == "running":
                    job.update(status="interrupted", recovery="pending",
                               output="서버 중단. 외부 부작용을 확인한 후 새 실행을 요청하세요.")
        self.save()

    def save(self):
        temp = self.directory / "state.tmp"
        with temp.open("w", encoding="utf-8") as handle:
            os.chmod(temp, 0o600)
            json.dump(self.state, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, self.path)


class Hub:
    def __init__(self, store, config, root=ROOT):
        self.store, self.config, self.root = store, config, Path(root)
        self.processes = {}
        self.workers = []
        self.closed = False

    def snapshot(self):
        with self.store.lock:
            result = copy.deepcopy(self.store.state)
        # The public view needs logical IDs, not private configured paths or argv.
        result["projects"] = list(self.config["projects"])
        result["drivers"] = list(self.config["drivers"])
        result["stamp"] = self.stamp()
        result["capabilities"] = {"auto_dispatch": False, "canonical_write": False}
        return result

    @staticmethod
    def needs_recovery(job):
        return job["status"] in ("interrupted", "timed_out") and job.get("recovery", "pending") == "pending"

    def board(self):
        """Build an allowlisted observation projection, never redact a full snapshot."""
        with self.store.lock:
            rooms = []
            for ordinal, room in enumerate(self.store.state["rooms"].values(), 1):
                jobs = list(room["jobs"].values())
                running = sum(j["status"] == "running" for j in jobs)
                pending = sum(j["status"] == "pending" for j in jobs)
                recovery = sum(self.needs_recovery(j) for j in jobs)
                status = ("closed" if room["closed"] else "paused" if room["paused"] else
                          "running" if running else "recovery" if recovery else "approval" if pending else "idle")
                rooms.append({"alias": f"Room {ordinal:02}", "status": status,
                              "members": sum(m["active"] for m in room["members"].values()),
                              "running": running, "pending": pending, "recovery": recovery,
                              "tx_count": room["tx_count"], "tx_limit": 10})
            return {"rooms": rooms, "totals": {"rooms": len(rooms),
                    "running": sum(r["running"] for r in rooms),
                    "pending": sum(r["pending"] for r in rooms),
                    "recovery": sum(r["recovery"] for r in rooms)}}

    def stamp(self):
        for line in (self.root / "INDEX.md").read_text().splitlines():
            if "규칙 버전:" in line:
                return line
        raise ValueError("INDEX 규칙 스탬프가 없습니다.")

    def room(self, room_id):
        room = self.store.state["rooms"].get(room_id)
        if room is None:
            raise ValueError("방을 찾을 수 없습니다.")
        return room

    def member(self, room, member_id):
        member = room["members"].get(member_id)
        if member is None or not member["active"]:
            raise ValueError("활성 멤버를 찾을 수 없습니다.")
        return member

    def event(self, room, kind, body):
        room["events"].append({"id": identifier("e-"), "at": now(), "kind": kind, "text": body})

    def action(self, data):
        with self.store.lock:
            if self.closed:
                raise ValueError("서버가 종료 중입니다.")
            action = data.get("action")
            if action == "create_room":
                rid = identifier(datetime.now(timezone.utc).strftime("%Y-%m-%d-"))
                self.store.state["rooms"][rid] = {
                    "id": rid, "title": text(data.get("title"), 160),
                    "goal": text(data.get("goal")), "initiative": str(data.get("initiative", ""))[:120],
                    "opened": now(), "closed": False, "members": {}, "messages": [], "notes": [],
                    "events": [], "jobs": {}, "tx": transaction(), "tx_count": 0,
                    "paused": False, "stamp": self.stamp(),
                }
                result = {"room_id": rid}
            else:
                room = self.room(data.get("room_id"))
                if room["closed"]:
                    raise ValueError("종료된 방은 읽기와 내보내기만 가능합니다.")
                result = self.room_action(room, action, data)
            self.store.save()
            return result or {}

    def room_action(self, room, action, data):
        if action == "add_member":
            mid = identifier("m-")
            project = data.get("project", "")
            if project and project not in self.config["projects"]:
                raise ValueError("등록되지 않은 실행 프로젝트입니다.")
            role = data.get("role", "worker")
            if role not in ("coordinator", "worker", "reviewer", "observer"):
                raise ValueError("잘못된 역할입니다.")
            room["members"][mid] = {"id": mid, "name": text(data.get("name"), 80), "project": project,
                                    "role": role, "active": True, "received": 0}
            self.event(room, "member", f"{mid} 입장 · {role} · {project or '미배정'}")
            return {"member_id": mid}
        if action == "message":
            sender = data.get("sender", "owner")
            body = text(data.get("text"))
            targets = data.get("targets", [])
            if not isinstance(targets, list) or len(targets) != len(set(targets)):
                raise ValueError("수신자 ID 배열이 필요하며 중복은 허용하지 않습니다.")
            members = [self.member(room, t) for t in targets]
            if sender != "owner":
                self.member(room, sender)
                if sender in targets:
                    raise ValueError("자기 자신에게 전달할 수 없습니다.")
                if room["paused"] or room["tx_count"] >= 10:
                    raise ValueError("통신 예산이 종료되었습니다. 사람의 새 프롬프트가 필요합니다.")
                if room["tx_count"] + len(targets) > 10 or any(m["received"] >= 5 for m in members):
                    raise ValueError("팬아웃이 통신 예산을 초과합니다. 전달하지 않았습니다.")
                room["tx_count"] += len(targets)
                for member in members:
                    member["received"] += 1
                room["paused"] = room["tx_count"] >= 10 or any(m["received"] >= 5 for m in members)
            else:
                # Only directly addressed recipients receive a new human prompt.
                room["tx"] = transaction()
                room["tx_count"] = 0
                for member in members:
                    member["received"] = 0
                room["paused"] = any(m["active"] and m["received"] >= 5 for m in room["members"].values())
            room["messages"].append({"id": identifier("msg-"), "at": now(), "sender": sender,
                                      "targets": targets, "text": body, "tx": room["tx"],
                                      "tx_count": room["tx_count"]})
        elif action == "note":
            author = data.get("author", "owner")
            if author != "owner":
                self.member(room, author)
            room["notes"].append({"id": identifier("n-"), "at": now(), "author": author,
                                   "title": text(data.get("title"), 160), "text": text(data.get("text"))})
        elif action == "leave":
            member = self.member(room, data.get("member_id"))
            if any(j["member_id"] == member["id"] and j["status"] == "running" for j in room["jobs"].values()):
                raise ValueError("실행 중인 멤버는 먼저 실행을 중지해야 합니다.")
            summary = text(data.get("summary"))
            member["active"] = False
            for job in room["jobs"].values():
                if job["member_id"] == member["id"] and job["status"] == "pending":
                    job["status"] = "rejected"
            self.event(room, "handoff", f"{member['id']} 퇴장 · {summary}")
        elif action == "close":
            if any(j["status"] == "running" for j in room["jobs"].values()):
                raise ValueError("실행 중인 작업을 먼저 중지해야 합니다.")
            for job in room["jobs"].values():
                if job["status"] == "pending":
                    job["status"] = "rejected"
            room["closed"] = True
            self.event(room, "close", text(data.get("summary")))
        elif action == "request_run":
            member = self.member(room, data.get("member_id"))
            if room["paused"] or member["received"] >= 5:
                raise ValueError("통신 예산 중단 상태에서 새 실행을 요청할 수 없습니다.")
            driver = data.get("driver")
            if driver not in self.config["drivers"] or member["project"] not in self.config["projects"]:
                raise ValueError("로컬 driver와 실행 프로젝트를 먼저 설정하세요.")
            if member["role"] == "observer":
                raise ValueError("observer는 실행할 수 없습니다.")
            if member["role"] == "reviewer" and self.config["drivers"][driver].get("mode") != "read-only":
                raise ValueError("reviewer에는 read-only 실행기만 연결할 수 있습니다.")
            jid = identifier("job-")
            room["jobs"][jid] = {"id": jid, "member_id": member["id"], "driver": driver,
                                   "project": member["project"], "prompt": text(data.get("prompt")),
                                   "status": "pending", "at": now(), "output": "", "stamp": self.stamp()}
            self.event(room, "approval", f"{jid} 실행 승인 대기")
            return {"job_id": jid}
        elif action == "recover_job":
            job = room["jobs"].get(data.get("job_id"))
            if not job or not self.needs_recovery(job):
                raise ValueError("복구 판단이 필요한 중단 실행을 찾을 수 없습니다.")
            if data.get("reviewed") is not True:
                raise ValueError("Git·외부 상태·부분 부작용을 먼저 확인하세요.")
            decision = data.get("decision")
            if decision == "discard":
                job.update(recovery="discarded", reviewed_at=now())
                self.event(room, "recovery", f"{job['id']} 재실행 안 함 · 부분 부작용 확인")
            elif decision == "prepare":
                if room["stamp"] != self.stamp():
                    raise ValueError("INDEX가 변경되었습니다. 새 규칙을 읽고 새 방에서 이어가세요.")
                result = self.room_action(room, "request_run", {"member_id": job["member_id"],
                                          "driver": job["driver"], "prompt": data.get("prompt")})
                room["jobs"][result["job_id"]]["source_job"] = job["id"]
                job.update(recovery="reviewed", reviewed_at=now(), replacement_job=result["job_id"])
                self.event(room, "recovery", f"{job['id']} → {result['job_id']} 새 승인 대기")
                return result
            else:
                raise ValueError("복구 결정은 prepare 또는 discard입니다.")
        elif action in ("approve", "reject", "cancel"):
            job = room["jobs"].get(data.get("job_id"))
            if job is None:
                raise ValueError("실행 요청을 찾을 수 없습니다.")
            if action == "cancel":
                if job["status"] != "running":
                    raise ValueError("실행 중인 요청만 중지할 수 있습니다.")
                process = self.processes.get(job["id"])
                job["cancel_requested"] = True
                if process:
                    self.stop_process(process)
                self.event(room, "cancel", f"{job['id']} 중지 요청 · 부분 부작용 확인 필요")
                return
            if job["status"] != "pending":
                raise ValueError("이미 처리된 승인입니다.")
            if action == "reject":
                job["status"] = "rejected"
                self.event(room, "approval", f"{job['id']} 거절")
                return
            member = self.member(room, job["member_id"])
            if room["paused"] or member["received"] >= 5 or room["stamp"] != self.stamp() or job["stamp"] != self.stamp():
                raise ValueError("예산 또는 INDEX 규칙이 변경되었습니다. 새 방에서 지침을 다시 확인하세요.")
            # A project is a single writable resource, even across rooms.
            if any(j["status"] == "running" and j["project"] == job["project"]
                   for r in self.store.state["rooms"].values() for j in r["jobs"].values()):
                raise ValueError("이 프로젝트에서 다른 실행이 진행 중입니다.")
            job["status"] = "running"
            job["started"] = now()
            self.event(room, "approval", f"{job['id']} 사람 승인 · 실행 시작")
            # Persist the consumed approval before launching an external command.
            self.store.save()
            worker = threading.Thread(target=self.execute, args=(room["id"], job["id"]), daemon=True)
            self.workers.append(worker)
            worker.start()
        else:
            raise ValueError("알 수 없는 동작입니다.")

    @staticmethod
    def stop_process(process):
        try:
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
        except ProcessLookupError:
            pass

    def execute(self, room_id, job_id):
        output = bytearray()
        result = "failed"
        exit_code = None
        try:
            with self.store.lock:
                job = copy.deepcopy(self.room(room_id)["jobs"][job_id])
                driver = self.config["drivers"][job["driver"]]
                member = self.room(room_id)["members"][job["member_id"]]
                if job.get("cancel_requested") or self.closed:
                    raise ValueError("실행 시작 전 중지됨")
                primary(self.root)
                # stdin is the only agent-controlled input; argv is never interpolated.
                process = subprocess.Popen(driver["argv"], cwd=self.config["projects"][job["project"]],
                                           stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           start_new_session=(os.name == "posix"))
                self.processes[job_id] = process

            def read_output():
                while True:
                    chunk = process.stdout.read(4096)
                    if not chunk:
                        break
                    remaining = MAX_OUTPUT - len(output)
                    if remaining > 0:
                        output.extend(chunk[:remaining])

            reader = threading.Thread(target=read_output, daemon=True)
            reader.start()

            def write_input():
                try:
                    context = ("Shared harness INDEX.md, complete current source:\n\n"
                               + (self.root / "INDEX.md").read_text()
                               + f"\n\nShared harness location: {self.root}. "
                               f"Project: {job['project']}. Role: {member['role']}. "
                               "This approval covers only this prompt; push, merge, deployment and external messages "
                               "need separate human authorization. Report observed verification and partial effects.\n\n"
                               + job["prompt"])
                    process.stdin.write(context.encode())
                    process.stdin.close()
                except (BrokenPipeError, OSError):
                    pass

            writer = threading.Thread(target=write_input, daemon=True)
            writer.start()
            try:
                exit_code = process.wait(timeout=driver["timeout"])
                result = "finished" if exit_code == 0 else "failed"
            except subprocess.TimeoutExpired:
                self.stop_process(process)
                process.wait()
                result = "timed_out"
            # A command invocation owns its process group; descendants cannot outlive it.
            if os.name == "posix":
                self.stop_process(process)
            reader.join(timeout=2)
            writer.join(timeout=2)
            if not reader.is_alive():
                process.stdout.close()
            if not writer.is_alive() and not process.stdin.closed:
                process.stdin.close()
        except Exception as error:
            # Do not expose private command/path details in the shared view.
            output.extend(f"실행 오류 ({type(error).__name__}); 로컬 설정과 부분 부작용을 확인하세요.".encode())
        finally:
            with self.store.lock:
                self.processes.pop(job_id, None)
                job = self.room(room_id)["jobs"][job_id]
                if job.get("cancel_requested") or self.closed:
                    result = "interrupted"
                job.update(status=result, ended=now(), exit_code=exit_code,
                           output=output.decode("utf-8", errors="replace"),
                           output_limit_bytes=MAX_OUTPUT)
                if result in ("interrupted", "timed_out"):
                    job["recovery"] = "pending"
                self.event(self.room(room_id), "run", f"{job_id} {result} · 업무 검증은 별도 확인")
                self.store.save()

    def shutdown(self):
        with self.store.lock:
            self.closed = True
            for process in list(self.processes.values()):
                self.stop_process(process)
        deadline = time.monotonic() + 5
        for worker in self.workers:
            worker.join(timeout=max(0, deadline - time.monotonic()))
        return not any(worker.is_alive() for worker in self.workers)

    def approval_details(self, room_id, job_id):
        with self.store.lock:
            job = self.room(room_id)["jobs"].get(job_id)
            if not job:
                raise ValueError("실행 요청을 찾을 수 없습니다.")
            driver = self.config["drivers"][job["driver"]]
            effective = (cli_command(driver["type"], driver["mode"], driver.get("cli"),
                                     driver.get("model"), driver.get("effort"))
                         if driver.get("type") in ("claude", "codex") else driver["argv"])
            return {"argv": driver["argv"], "effective_argv": effective,
                    "cwd": self.config["projects"][job["project"]], "prompt": job["prompt"],
                    "timeout": self.config["drivers"][job["driver"]]["timeout"]}

    def export(self, room_id):
        with self.store.lock:
            room = copy.deepcopy(self.room(room_id))
        lines = [f"# {room['title']}", "", "> 비정본 룸 기록. 공개 위험 검토 전 공유·커밋 금지.",
                 f"\n- room: {room['id']}", f"- exported: {now()}", f"- initiative: {room['initiative'] or '-'}",
                 f"\n## 목표\n\n{room['goal']}", "\n## 멤버"]
        for m in room["members"].values():
            lines.append(f"- {m['id']} · {m['name']} · {m['project'] or '-'} · {m['role']}")
        lines.append("\n## 대화")
        for m in room["messages"]:
            lines.append(f"\n### {m['at']} · {m['sender']} → {', '.join(m['targets']) or '표시만'}\n\n{m['text']}")
        lines.append("\n## 노트")
        for n in room["notes"]:
            lines.append(f"\n### {n['title']} · {n['at']} · {n['author']}\n\n{n['text']}")
        lines.append("\n## 실행 결과")
        for j in room["jobs"].values():
            lines.append(f"\n### {j['id']} · {j['status']} · exit:{j.get('exit_code', '-')}\n\n{j['prompt']}\n\n{j['output']}")
        lines.append("\n## 이벤트")
        lines.extend(f"- {e['at']} · {e['kind']} · {e['text']}" for e in room["events"])
        return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # URLs and message bodies are not operational logs.

    def send(self, status, body, content_type="application/json; charset=utf-8"):
        payload = json.dumps(body, ensure_ascii=False).encode() if isinstance(body, dict) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(payload)

    def allowed(self, mutation=False):
        origin = f"http://127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
            self.send(403, {"error": "Host 거부"})
            return False
        if self.headers.get("Origin") not in (None, origin):
            self.send(403, {"error": "Origin 거부"})
            return False
        if self.headers.get("Sec-Fetch-Site") not in (None, "same-origin", "none"):
            self.send(403, {"error": "교차 사이트 요청 거부"})
            return False
        path = urlsplit(self.path).path
        if mutation or (path.startswith("/api/") and path != "/api/version"):
            token = self.headers.get("X-Room-Token", "")
            owner = hmac.compare_digest(token, self.server.token)
            viewer = path == "/api/board" and not mutation and hmac.compare_digest(token, self.server.view_token)
            if not (owner or viewer):
                self.send(403, {"error": "로컬 룸 토큰 필요"})
                return False
        return True

    def do_GET(self):
        if not self.allowed():
            return
        path = urlsplit(self.path).path
        try:
            if path == "/api/state":
                result = self.server.hub.snapshot()
                result.update(version=self.server.version, board_url="/board#" + self.server.view_token)
                self.send(200, result)
            elif path == "/api/board":
                result = self.server.hub.board()
                result["version"] = self.server.version
                self.send(200, result)
            elif path == "/api/version":
                self.send(200, {"version": self.server.version})
            elif path == "/api/export":
                from urllib.parse import parse_qs
                rid = parse_qs(urlsplit(self.path).query).get("room_id", [""])[0]
                self.send(200, self.server.hub.export(rid).encode(), "text/markdown; charset=utf-8")
            else:
                asset = self.server.assets.get(path)
                if not asset:
                    self.send(404, {"error": "찾을 수 없습니다."})
                    return
                self.send(200, asset[0], asset[1])
        except (ValueError, OSError):
            self.send(400, {"error": "조회할 수 없습니다."})

    def do_POST(self):
        if not self.allowed(mutation=True):
            return
        try:
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("JSON 요청이 필요합니다.")
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 100000:
                raise ValueError("요청 크기 초과")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("JSON 객체가 필요합니다.")
            if self.path == "/api/action":
                self.send(200, self.server.hub.action(data))
            elif self.path == "/api/approval-details":
                self.send(200, self.server.hub.approval_details(data.get("room_id"), data.get("job_id")))
            else:
                self.send(404, {"error": "찾을 수 없습니다."})
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
            self.send(400, {"error": str(error)})
        except Exception:
            self.send(500, {"error": "상태 저장 실패. 재시도 전에 현재 상태를 확인하세요."})


class LocalServer(ThreadingHTTPServer):
    def server_bind(self):
        # No reverse-DNS lookup is needed for the fixed loopback address.
        socketserver.TCPServer.server_bind(self)
        self.server_name = "127.0.0.1"
        self.server_port = self.server_address[1]


def make_server(hub, port=8765, web_dir=WEB):
    assets = {url: ((web_dir / filename).read_bytes(), mime) for url, (filename, mime) in ASSETS.items()}
    digest = hashlib.sha256()
    for url in sorted(assets):
        digest.update(url.encode() + b"\0" + assets[url][0])
    for source in (Path(__file__), Path(__file__).with_name("drivers.py")):
        digest.update(source.read_bytes())
    server = LocalServer(("127.0.0.1", port), Handler)
    server.daemon_threads = True
    server.hub, server.token = hub, secrets.token_urlsafe(32)
    server.view_token = secrets.token_urlsafe(32)
    server.assets, server.version = assets, digest.hexdigest()[:16]
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "local" / "room")
    parser.add_argument("--config", type=Path, help="ignored local JSON with projects and drivers")
    args = parser.parse_args()
    primary(ROOT)
    directory = args.data_dir.expanduser().resolve()
    # Tracked runtime state is never a replacement for the shared records.
    if (directory == ROOT or ROOT in directory.parents) and not directory.is_relative_to(ROOT / "local"):
        parser.error("저장소 내부 데이터는 gitignore된 local/ 아래에 두세요.")
    config = load_config(args.config, ROOT)
    # One server per data directory, including across processes.
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock_path = directory / "server.lock"
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        parser.error("동일 데이터의 서버 lock이 있습니다. 기존 서버·부분 실행을 확인하고 종료 후 제거하세요.")
    os.write(lock_fd, str(os.getpid()).encode())
    os.close(lock_fd)
    hub = None
    try:
        store = Store(directory)
        hub = Hub(store, config)
        server = make_server(hub, args.port)
        print(f"Room: http://127.0.0.1:{server.server_port}/#{server.token}", flush=True)
        print("로컬 토큰은 공유하지 마세요. Ctrl+C로 서버와 실행 중인 작업을 중지합니다.", flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        clean_stop = hub.shutdown() if hub else True
        if "server" in locals():
            server.server_close()
        if clean_stop:
            lock_path.unlink(missing_ok=True)
        else:
            print("실행 종료를 확정하지 못했습니다. lock을 보존했습니다. 부분 상태를 확인하세요.", file=sys.stderr)


if __name__ == "__main__":
    main()
