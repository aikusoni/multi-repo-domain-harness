import concurrent.futures
import http.client
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from room.server import Hub, Store, load_config, make_server, primary


class RoomTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "harness"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "INDEX.md").write_text("# Rules\n**규칙 버전: r0001**\n")
        self.project = self.base / "product"
        self.project.mkdir()
        self.config = {"projects": {"product": str(self.project)}, "drivers": {
            "echo": {"argv": [sys.executable, "-c", "import sys; print(sys.stdin.read())"], "timeout": 5},
            "slow": {"argv": [sys.executable, "-c", "import time; time.sleep(10)"], "timeout": 1},
            "fail": {"argv": [sys.executable, "-c", "raise SystemExit(4)"], "timeout": 5},
        }}
        self.store = Store(self.base / "data")
        self.hub = Hub(self.store, self.config, self.root)
        self.rid = self.hub.action({"action": "create_room", "title": "Fixture", "goal": "Verify"})["room_id"]
        self.mids = [self.act("add_member", name="Member", project="product")["member_id"] for _ in range(3)]

    def tearDown(self):
        self.hub.shutdown()
        deadline = time.monotonic() + 5
        while self.hub.processes and time.monotonic() < deadline:
            time.sleep(.01)
        self.temp.cleanup()

    def act(self, action, **kwargs):
        return self.hub.action({"action": action, "room_id": self.rid, **kwargs})

    def job(self, driver="echo", prompt="hello"):
        return self.act("request_run", member_id=self.mids[0], driver=driver, prompt=prompt)["job_id"]

    def finish(self, jid):
        deadline = time.monotonic() + 7
        while time.monotonic() < deadline:
            j = self.hub.snapshot()["rooms"][self.rid]["jobs"][jid]
            if j["status"] != "running":
                return j
            time.sleep(.01)
        self.fail("job did not finish")

    def test_no_dispatch_until_owner_approval(self):
        jid = self.job(prompt="$(touch unwanted) `echo input`")
        self.assertEqual(self.hub.room(self.rid)["jobs"][jid]["status"], "pending")
        self.assertFalse(self.hub.processes)
        self.act("approve", job_id=jid)
        result = self.finish(jid)
        self.assertEqual(result["status"], "finished")
        self.assertIn("$(touch unwanted)", result["output"])
        self.assertFalse((self.project / "unwanted").exists())

    def test_approval_consumed_once_under_race(self):
        jid = self.job("slow")
        def approve():
            try:
                self.act("approve", job_id=jid)
                return True
            except ValueError:
                return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            results = list(pool.map(lambda _: approve(), range(2)))
        self.assertEqual(results.count(True), 1)
        self.assertEqual(self.finish(jid)["status"], "timed_out")

    def test_single_project_execution_across_rooms(self):
        jid = self.job("slow")
        self.act("approve", job_id=jid)
        other = self.hub.action({"action":"create_room", "title":"Other", "goal":"Verify"})["room_id"]
        mid = self.hub.action({"action":"add_member", "room_id":other, "name":"Other", "project":"product"})["member_id"]
        jid2 = self.hub.action({"action":"request_run", "room_id":other, "member_id":mid, "driver":"echo", "prompt":"test"})["job_id"]
        with self.assertRaisesRegex(ValueError, "다른 실행"):
            self.hub.action({"action":"approve", "room_id":other, "job_id":jid2})
        self.finish(jid)

    def test_fanout_budget_atomic_and_fifth_receive(self):
        for _ in range(4):
            self.act("message", sender=self.mids[0], targets=self.mids[1:], text="new evidence")
        before = self.hub.snapshot()
        with self.assertRaises(ValueError):
            self.act("message", sender=self.mids[0], targets=[*self.mids[1:], self.mids[0]], text="invalid")
        self.assertEqual(before, self.hub.snapshot())
        self.act("message", sender=self.mids[0], targets=self.mids[1:], text="fifth")
        self.assertTrue(self.hub.room(self.rid)["paused"])
        self.assertEqual(self.hub.room(self.rid)["tx_count"], 10)
        with self.assertRaises(ValueError):
            self.act("message", sender=self.mids[0], targets=[self.mids[1]], text="sixth")
        with self.assertRaises(ValueError):
            self.job()
        self.act("message", sender="owner", targets=self.mids[1:], text="Continue with the new scope")
        self.assertFalse(self.hub.room(self.rid)["paused"])
        self.assertEqual(self.hub.room(self.rid)["tx_count"], 0)

    def test_fanout_overflow_has_no_partial_delivery(self):
        room = self.hub.room(self.rid)
        room["tx_count"] = 9
        with self.assertRaisesRegex(ValueError, "ファン|팬아웃"):
            self.act("message", sender=self.mids[0], targets=self.mids[1:], text="overflow")
        self.assertEqual(room["tx_count"], 9)
        self.assertEqual(len(room["messages"]), 0)
        self.assertEqual(room["members"][self.mids[1]]["received"], 0)

    def test_human_prompt_resets_only_recipients(self):
        room = self.hub.room(self.rid)
        room["members"][self.mids[2]]["received"] = 5
        room["paused"] = True
        self.act("message", sender="owner", targets=[self.mids[1]], text="new prompt")
        self.assertTrue(room["paused"])
        self.assertEqual(room["members"][self.mids[2]]["received"], 5)

    def test_stamp_change_invalidates_pending_approval(self):
        jid = self.job()
        (self.root / "INDEX.md").write_text("**규칙 버전: r0002**")
        with self.assertRaisesRegex(ValueError, "INDEX"):
            self.act("approve", job_id=jid)
        self.assertEqual(self.hub.room(self.rid)["jobs"][jid]["status"], "pending")

    def test_reviewer_cannot_use_write_driver(self):
        self.hub.room(self.rid)["members"][self.mids[0]]["role"] = "reviewer"
        self.config["drivers"]["echo"]["mode"] = "workspace-write"
        with self.assertRaisesRegex(ValueError,"read-only"):
            self.job()
        self.config["drivers"]["echo"]["mode"] = "read-only"
        self.assertTrue(self.job())

    def test_failure_timeout_cancel_are_distinct(self):
        jid = self.job("fail")
        self.act("approve", job_id=jid)
        result = self.finish(jid)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["exit_code"], 4)
        jid = self.job("slow")
        self.act("approve", job_id=jid)
        self.act("cancel", job_id=jid)
        self.assertEqual(self.finish(jid)["status"], "interrupted")

    def test_recovery_does_not_replay_running_jobs(self):
        jid = self.job()
        self.hub.room(self.rid)["jobs"][jid]["status"] = "running"
        self.store.save()
        recovered = Store(self.base / "data")
        self.assertEqual(recovered.state["rooms"][self.rid]["jobs"][jid]["status"], "interrupted")

    def test_export_and_close_do_not_write_harness_records(self):
        self.act("note", title="Handoff", text="Partial verification")
        jid = self.job()
        self.act("close", summary="See task record")
        self.assertEqual(self.hub.room(self.rid)["jobs"][jid]["status"], "rejected")
        transcript = self.hub.export(self.rid)
        self.assertIn("비정본", transcript)
        self.assertIn("Partial verification", transcript)
        self.assertIn("UTC", transcript)
        self.assertFalse((self.root / "journal").exists())
        with self.assertRaises(ValueError):
            self.act("note", title="Late", text="Late")

    def test_local_config_and_primary_boundary(self):
        p = self.base / "config.json"
        p.write_text(json.dumps({"projects":{"harness":str(self.root)},"drivers":{}}))
        with self.assertRaises(ValueError):
            load_config(p,self.root)
        primary(self.root)
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "-qm", "init"],check=True)
        linked = self.base / "linked"
        subprocess.run(["git", "-C", str(self.root), "worktree", "add", "--detach", "-q",str(linked)],check=True)
        with self.assertRaisesRegex(ValueError,"primary"):
            primary(linked)

    def test_output_is_bounded(self):
        self.config["drivers"]["large"] = {"argv":[sys.executable,"-c","print('x'*1000000)"],"timeout":5}
        jid = self.job("large")
        self.act("approve",job_id=jid)
        output = self.finish(jid)["output"]
        self.assertLessEqual(len(output.encode()),64000)

    def test_http_security_and_static_routes(self):
        server = make_server(self.hub,0)
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        def request(path, method="GET", data=None, headers=None):
            conn = http.client.HTTPConnection("127.0.0.1",server.server_port)
            h = {"X-Room-Token":server.token, "Content-Type":"application/json", **(headers or {})}
            conn.request(method,path,json.dumps(data) if data else None,h)
            response=conn.getresponse()
            result=(response.status,response.read(),dict(response.getheaders()))
            conn.close()
            return result
        try:
            self.assertEqual(request("/")[0],200)
            self.assertEqual(request("/app.js")[0],200)
            self.assertEqual(request("/style.css")[0],200)
            self.assertEqual(request("/../INDEX.md")[0],404)
            self.assertEqual(request("/api/state",headers={"X-Room-Token":"bad"})[0],403)
            self.assertEqual(request("/api/state",headers={"Host":"evil.invalid"})[0],403)
            self.assertEqual(request("/api/state",headers={"Origin":"https://evil.invalid"})[0],403)
            self.assertEqual(request("/api/state",headers={"Sec-Fetch-Site":"cross-site"})[0],403)
            data = {"action":"note","room_id":self.rid,"title":"HTTP","text":"Note"}
            self.assertEqual(request("/api/action","POST",data)[0],200)
            self.assertIn(b"frame-ancestors",request("/")[2]["Content-Security-Policy"].encode())
            snapshot = json.loads(request("/api/state")[1])
            self.assertEqual(snapshot["projects"],["product"])
            self.assertNotIn(str(self.project),json.dumps(snapshot))
            self.assertNotIn("argv",json.dumps(snapshot))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
