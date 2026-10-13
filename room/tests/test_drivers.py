import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from room.drivers import command, parse_event, preflight
from room.server import load_config


class DriverTest(unittest.TestCase):
    def test_codex_explicit_sandbox_and_no_bypass(self):
        argv = command("codex", "read-only", model="chosen-model", effort="high")
        self.assertIn("read-only", argv)
        self.assertIn("--json", argv)
        self.assertEqual(argv[-1], "-")
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", argv)
        self.assertIn('model_reasoning_effort="high"', argv)
        self.assertIn("workspace-write", command("codex", "workspace-write"))

    def test_claude_restricted_read_and_edit_profiles(self):
        read = command("claude")
        write = command("claude", "workspace-write")
        self.assertIn("--restricted", read)
        self.assertIn("dontAsk", read)
        self.assertIn("none", read)
        self.assertIn("--strict-mcp-config", read)
        self.assertIn("Read,Glob,Grep", read)
        self.assertNotIn("Read,Glob,Grep,Edit,Write", read)
        self.assertIn("Read,Glob,Grep,Edit,Write", write)
        self.assertIn("acceptEdits", write)
        self.assertNotIn("Bash", ",".join(write))
        self.assertNotIn("bypassPermissions", write)

    def test_normalize_provider_results_and_failures(self):
        self.assertEqual(parse_event("codex",{"type":"item.completed","item":{"type":"agent_message","text":"Verified"}}),("Verified",False,True))
        self.assertEqual(parse_event("codex",{"type":"turn.failed"}),("",True,False))
        self.assertEqual(parse_event("claude",{"type":"result","result":"Partial","is_error":True}),("Partial",True,True))
        self.assertEqual(parse_event("codex",{"type":"item.completed","item":{"type":"command_execution"}}),("",False,False))

    def test_config_generates_separate_adapters(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/"config.json"
            p.write_text(json.dumps({"projects":{},"drivers":{"a":{"type":"claude"},"b":{"type":"codex","mode":"workspace-write"}}}))
            result = load_config(p,Path(temp)/"harness")["drivers"]
            self.assertIn("claude",result["a"]["argv"])
            self.assertIn("codex",result["b"]["argv"])
            self.assertEqual(result["a"]["mode"],"read-only")
            p.write_text(json.dumps({"drivers":{"bad":{"type":"codex","mode":"danger-full-access"}}}))
            with self.assertRaises(ValueError):
                load_config(p,Path(temp)/"harness")

    def test_missing_cli_is_explicit_failure(self):
        with self.assertRaises(ValueError):
            preflight("codex","nonexistent-room-fixture-cli")

    @unittest.skipIf(os.name == "nt", "POSIX executable fixture; command/result contracts tested on all platforms")
    def test_real_adapter_process_with_fake_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            cli = Path(temp)/"fake-cli"
            cli.write_text(f"#!{sys.executable}\n" + "import sys,json\nif '--help' in sys.argv:\n print('--json --sandbox --restricted --permission-prompts --tools --output-format')\nelse:\n prompt=sys.stdin.read()\n if '--json' in sys.argv:\n  print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':prompt}}))\n else:\n  print(json.dumps({'type':'result','result':prompt,'is_error':False}))\n")
            cli.chmod(0o700)
            for provider in ("codex","claude"):
                result=subprocess.run([sys.executable,"-B","room/drivers.py","--provider",provider,"--cli",str(cli)],input="literal $(touch forbidden)",capture_output=True,text=True,timeout=10)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertIn("literal $(touch forbidden)",result.stdout)
            cli.write_text(f"#!{sys.executable}\n" + "import sys,json\nif '--help' in sys.argv: print('--json --sandbox')\nelse: print(json.dumps({'type':'turn.failed'}))\n")
            result=subprocess.run([sys.executable,"-B","room/drivers.py","--provider","codex","--cli",str(cli)],input="test",capture_output=True,text=True,timeout=10)
            self.assertNotEqual(result.returncode,0)


if __name__ == "__main__":
    unittest.main()
