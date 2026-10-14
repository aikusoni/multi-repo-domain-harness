import concurrent.futures
import http.client
import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest

from room.server import ASSETS, WEB, Hub, Store, make_server


class UpgradeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "harness"
        self.root.mkdir()
        (self.root / "INDEX.md").write_text("**규칙 버전: r0021**\n")
        self.marker = "PRIVATE-SENTINEL-NOT-FOR-OBSERVATION"
        self.config = {"projects": {self.marker:str(self.base)}, "drivers": {
            self.marker:{"argv":[self.marker],"mode":"read-only","timeout":1}}}
        self.store = Store(self.base/"data")
        self.hub = Hub(self.store,self.config,self.root)
        self.rid = self.hub.action({"action":"create_room","title":self.marker,"goal":self.marker,"initiative":self.marker})["room_id"]
        self.mid = self.act("add_member", name=self.marker, project=self.marker)["member_id"]
        self.jid = self.act("request_run",member_id=self.mid,driver=self.marker,prompt=self.marker)["job_id"]

    def tearDown(self):
        self.hub.shutdown()
        self.temp.cleanup()

    def act(self, action, **kwargs):
        return self.hub.action({"action":action,"room_id":self.rid,**kwargs})

    def interrupt(self):
        job=self.hub.room(self.rid)["jobs"][self.jid]
        job.update(status="interrupted",output=self.marker)

    def test_board_is_allowlisted_without_identity_or_text(self):
        self.act("message",text=self.marker)
        self.act("note",title=self.marker,text=self.marker)
        self.interrupt()
        view=self.hub.board()
        encoded=json.dumps(view)
        for private in (self.marker,self.rid,self.mid,self.jid,str(self.base)):
            self.assertNotIn(private,encoded)
        self.assertEqual(set(view),{"rooms","totals"})
        self.assertEqual(set(view["rooms"][0]),{"alias","status","members","running","pending","recovery","tx_count","tx_limit"})
        self.assertEqual(view["rooms"][0]["status"],"recovery")
        self.assertEqual(view["rooms"][0]["alias"],"Room 01")
        self.assertEqual(self.hub.snapshot()["rooms"][self.rid]["title"],self.marker)

    def test_recovery_needs_review_and_fresh_approval(self):
        self.interrupt()
        before=self.hub.snapshot()
        with self.assertRaises(ValueError):
            self.act("recover_job",job_id=self.jid,decision="prepare",prompt="New request")
        self.assertEqual(before,self.hub.snapshot())
        new=self.act("recover_job",job_id=self.jid,decision="prepare",reviewed=True,prompt="New safe request")["job_id"]
        self.assertEqual(self.hub.room(self.rid)["jobs"][new]["status"],"pending")
        self.assertFalse(self.hub.processes)
        self.assertEqual(self.hub.room(self.rid)["jobs"][new]["source_job"],self.jid)
        self.assertEqual(self.hub.board()["totals"]["recovery"],0)
        with self.assertRaises(ValueError):
            self.act("recover_job",job_id=self.jid,decision="prepare",reviewed=True,prompt="Duplicate")

    def test_recovery_race_is_consumed_once(self):
        self.interrupt()
        def prepare(_):
            try:
                self.act("recover_job",job_id=self.jid,decision="prepare",reviewed=True,prompt="New request")
                return True
            except ValueError:
                return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            self.assertEqual(list(pool.map(prepare,range(2))).count(True),1)
        self.assertEqual(len(self.hub.room(self.rid)["jobs"]),2)

    def test_discard_preserves_history_without_running(self):
        self.interrupt()
        self.act("recover_job",job_id=self.jid,decision="discard",reviewed=True)
        job=self.hub.room(self.rid)["jobs"][self.jid]
        self.assertEqual(job["status"],"interrupted")
        self.assertEqual(job["output"],self.marker)
        self.assertEqual(job["recovery"],"discarded")
        self.assertEqual(len(self.hub.room(self.rid)["jobs"]),1)

    def test_recovery_rechecks_budget_and_stamp(self):
        self.interrupt()
        self.hub.room(self.rid)["paused"]=True
        with self.assertRaises(ValueError):
            self.act("recover_job",job_id=self.jid,decision="prepare",reviewed=True,prompt="New")
        self.hub.room(self.rid)["paused"]=False
        (self.root/"INDEX.md").write_text("**규칙 버전: r0022**")
        with self.assertRaises(ValueError):
            self.act("recover_job",job_id=self.jid,decision="prepare",reviewed=True,prompt="New")
        self.assertTrue(self.hub.needs_recovery(self.hub.room(self.rid)["jobs"][self.jid]))

    def test_restart_preserves_recovery_without_replay(self):
        self.hub.room(self.rid)["jobs"][self.jid]["status"]="running"
        self.store.save()
        recovered=Hub(Store(self.base/"data"),self.config,self.root)
        self.assertEqual(recovered.board()["totals"]["recovery"],1)
        self.assertFalse(recovered.processes)

    def test_viewer_capability_and_frozen_assets_over_http(self):
        web=self.base/"web"
        shutil.copytree(WEB,web)
        server=make_server(self.hub,0,web_dir=web)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        def request(path,token=None,method="GET",data=None):
            conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=3)
            headers={"Content-Type":"application/json"}
            if token is not None:headers["X-Room-Token"]=token
            conn.request(method,path,json.dumps(data) if data else None,headers)
            response=conn.getresponse();result=(response.status,response.read());conn.close();return result
        try:
            for path in ASSETS:
                self.assertEqual(request(path)[0],200)
            original=request("/app.js")[1]
            (web/"app.js").write_text("CHANGED-AFTER-START")
            self.assertEqual(request("/app.js")[1],original)
            self.assertEqual(request("/api/board",server.view_token)[0],200)
            self.assertNotIn(self.marker.encode(),request("/api/board",server.view_token)[1])
            for path in ("/api/state","/api/export?room_id="+self.rid):
                self.assertEqual(request(path,server.view_token)[0],403)
            for path in ("/api/action","/api/approval-details"):
                self.assertEqual(request(path,server.view_token,"POST",{"action":"approve","room_id":self.rid,"job_id":self.jid})[0],403)
            self.assertEqual(request("/api/board")[0],403)
            version=json.loads(request("/api/version")[1])
            self.assertEqual(set(version),{"version"})
            owner=json.loads(request("/api/state",server.token)[1])
            self.assertEqual(owner["board_url"],"/board#"+server.view_token)
            second=make_server(self.hub,0,web_dir=web)
            self.assertNotEqual(second.version,server.version)
            self.assertNotEqual(second.view_token,server.view_token)
            second.server_close()
        finally:
            server.shutdown();server.server_close();thread.join()


if __name__ == "__main__":
    unittest.main()
