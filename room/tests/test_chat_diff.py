import json
from http.client import HTTPConnection
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlencode

from room import gitdiff
from room.evaluate import Fixture, http, http_server


class ChatDiffTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.f = Fixture(Path(self.temp.name))
        self.product = Path(self.f.config['projects']['product'])
        self.git('init', '-q')
        self.write('app.py', 'def greet():\n    return "before"\n')
        self.write('removed.txt', 'old\n')
        self.write('binary.bin', b'\0before')
        self.git('add', 'app.py', 'removed.txt', 'binary.bin')
        self.commit('Fixture baseline')
        self.base = self.git('rev-parse', 'HEAD').strip()
        self.write('app.py', 'def greet():\n    return "after"\n')
        (self.product / 'removed.txt').unlink()
        self.write('new file.txt', 'new\n')
        self.git('add', 'new file.txt')
        self.write('untracked.txt', 'excluded\n')
        self.write('binary.bin', b'\0after')

    def tearDown(self):
        self.f.hub.shutdown()
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                                        '-C', str(self.product), *args], text=True, stderr=subprocess.DEVNULL)

    def write(self, path, value):
        p = self.product / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(value if isinstance(value, bytes) else value.encode())

    def commit(self, message):
        self.git('add', '-u')
        self.git('commit', '-qm', message)

    def diff(self, **kwargs):
        return self.f.hub.diff(self.f.rid, 'product', **kwargs)

    def query(self, result, **kwargs):
        data = {'project': 'product', 'path': result['path'], 'base': result['base'], 'head': result['head'],
                'comparison': result['comparison'], 'digest': result['digest'], 'member_id': self.f.mid,
                'driver': 'read', 'question': 'What changed?'}
        return self.f.act('request_diff_question', **{**data, **kwargs})

    def test_working_files_and_exact_line_pairing(self):
        listing = self.diff()
        entries = {entry['path']: entry for entry in listing['files']}
        self.assertEqual(entries['app.py']['status'], 'M')
        self.assertEqual(entries['new file.txt']['status'], 'A')
        self.assertEqual(entries['removed.txt']['status'], 'D')
        self.assertNotIn('untracked.txt', entries)
        result = self.diff(path='app.py')
        self.assertEqual(result['rows'][0]['kind'], 'same')
        self.assertEqual(result['rows'][1]['old_line'], 2)
        self.assertIn('before', result['rows'][1]['old'])
        self.assertIn('after', result['rows'][1]['new'])
        self.assertIsNone(self.diff(path='removed.txt')['rows'][0]['new_line'])
        self.assertIsNone(self.diff(path='new file.txt')['rows'][0]['old_line'])

    def test_commit_pair_merge_base_and_no_changes(self):
        self.commit('Fixture target')
        target = self.git('rev-parse', 'HEAD').strip()
        self.assertEqual(len(self.diff(base=self.base, head=target, comparison='commits')['files']), 4)
        self.git('checkout', '-q', '-b', 'other', self.base)
        self.write('side.txt', 'side\n')
        self.git('add', 'side.txt')
        self.commit('Fixture side')
        listing = self.diff(base='HEAD', head=target, comparison='merge-base')
        self.assertEqual(listing['base'], self.base)
        self.assertNotIn('side.txt', [item['path'] for item in listing['files']])
        self.assertEqual(self.diff(base=target, head=target, comparison='commits')['files'], [])

    def test_binary_and_symlink_are_not_question_context(self):
        binary = self.diff(path='binary.bin')
        self.assertTrue(binary['binary'])
        with self.assertRaises(ValueError):
            gitdiff.question_references(binary)
        if os.name == 'posix':
            (self.product / 'link').symlink_to(Path(self.temp.name) / 'outside')
            self.git('add', 'link')
            self.assertTrue(self.diff(path='link')['unsupported'])

    def test_invalid_ref_path_unconnected_project_and_secrets_are_denied(self):
        for ref in ('--output=bad', 'HEAD;touch bad', '../other', 'HEAD:path', 'HEAD\n'):
            with self.assertRaises(ValueError):
                self.diff(base=ref)
        for path in ('../outside', '/etc/passwd', '.git/config', '.env', ':(glob)**', 'untracked.txt'):
            with self.assertRaises(ValueError):
                self.diff(path=path)
        for name in ('.env', '.env.local', 'private.pem', '.aws/credentials'):
            self.write(name, 'SYNTHETIC-NOT-A-CREDENTIAL\n')
            self.git('add', name)
        listing = self.diff()
        self.assertEqual(listing['excluded'], 4)
        self.assertFalse(any(item['path'].startswith('.env') for item in listing['files']))
        other = self.f.hub.action({'action': 'create_room', 'title': 'Other', 'goal': 'No connection'})['room_id']
        with self.assertRaises(ValueError):
            self.f.hub.diff(other, 'product')
        with self.assertRaises(ValueError):
            gitdiff.compare(self.product / 'nested')

    def test_external_diff_textconv_and_git_environment_are_not_executed(self):
        marker = Path(self.temp.name) / 'should-not-exist'
        self.git('config', 'diff.external', 'touch ' + str(marker))
        self.git('config', 'diff.test.textconv', 'touch ' + str(marker))
        self.write('.gitattributes', 'app.py diff=test\n')
        with patch.dict(os.environ, {'GIT_DIR': str(self.product / 'nonexistent')}):
            self.assertIn('after', self.diff(path='app.py')['rows'][1]['new'])
        self.assertFalse(marker.exists())

    def test_comparison_preserves_index_refs_and_working_bytes(self):
        before = (self.product / '.git/index').read_bytes(), self.git('rev-parse', 'HEAD'), (self.product / 'app.py').read_bytes()
        self.diff(path='app.py')
        after = (self.product / '.git/index').read_bytes(), self.git('rev-parse', 'HEAD'), (self.product / 'app.py').read_bytes()
        self.assertEqual(before, after)

    def test_working_clean_filter_cannot_execute(self):
        marker = Path(self.temp.name) / 'filter-should-not-exist'
        self.git('config', 'filter.test.clean', 'touch ' + str(marker))
        self.write('.gitattributes', 'app.py filter=test\n')
        with self.assertRaisesRegex(ValueError, 'filter'):
            self.diff(path='app.py')
        self.assertFalse(marker.exists())
        self.assertEqual(self.diff(base=self.base, head=self.base, comparison='commits')['files'], [])

    def test_limits_newline_and_selection_validation(self):
        self.write('app.py', 'def greet():\n    return "after"')
        result = self.diff(path='app.py')
        self.assertTrue(result['newline_changed'])
        refs = gitdiff.question_references(result, {'new': [2, 2]})
        self.assertIn('after', ''.join(refs))
        self.assertNotIn('def greet', ''.join(refs))
        for selection in ({'new': [0, 2]}, {'old': [2, 1]}, {'new': [1, 999]}, {'new': [True, 2]}, ['bad'], [], False):
            with self.assertRaises(ValueError):
                gitdiff.question_references(result, selection)
        with patch('room.gitdiff.FILE_LIMIT', 10):
            with self.assertRaises(ValueError):
                self.diff(path='app.py')
        with patch('room.gitdiff.LINE_LIMIT', 1):
            with self.assertRaises(ValueError):
                self.diff(path='app.py')
        with patch('room.gitdiff.LIST_LIMIT', 1):
            with self.assertRaises(ValueError):
                self.diff()

    def test_working_path_cannot_escape_through_parent_symlink(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (outside / 'value').write_text('PRIVATE-SYNTHETIC')
        (self.product / 'escape').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            gitdiff.working_bytes(self.product, 'escape/value')

    def test_question_requires_matching_fingerprint_read_driver_and_fresh_approval(self):
        result = self.diff(path='app.py')
        before = self.f.hub.snapshot()
        for kwargs in ({'driver': 'write'}, {'digest': 'stale'}, {'member_id': 'missing'}):
            with self.assertRaises(ValueError):
                self.query(result, **kwargs)
        self.assertEqual(before, self.f.hub.snapshot())
        jid = self.query(result, selection={'new': [2, 2]})['job_id']
        job = self.f.hub.room(self.f.rid)['jobs'][jid]
        self.assertEqual(job['status'], 'pending')
        self.assertEqual(job['skill'], 'investigate')
        self.assertIn('after', ''.join(job['references']))
        self.assertFalse(self.f.hub.processes)
        self.assertNotIn('after', json.dumps(self.f.hub.run_status(self.f.rid, jid)))
        self.write('app.py', 'changed again\n')
        with self.assertRaisesRegex(ValueError, '바뀌었'):
            self.query(result)

    def test_reply_is_same_room_and_budgeted_without_copying_source(self):
        self.f.act('message', sender=self.f.mid, text='Source fixture')
        source = self.f.hub.room(self.f.rid)['messages'][-1]
        self.f.act('message', reply_to=source['id'], text='Owner reply')
        reply = self.f.hub.room(self.f.rid)['messages'][-1]
        self.assertEqual(reply['targets'], [self.f.mid])
        self.assertEqual(reply['reply_to'], source['id'])
        self.assertEqual(reply['text'], 'Owner reply')
        self.assertIn(source['id'], self.f.hub.export(self.f.rid))
        other = self.f.act('add_member', name='Other', project='product')['member_id']
        for _ in range(5):
            self.f.act('message', sender=other, reply_to=source['id'], text='Peer reply')
        self.assertEqual(self.f.hub.room(self.f.rid)['members'][self.f.mid]['received'], 5)
        self.assertTrue(self.f.hub.room(self.f.rid)['paused'])
        with self.assertRaises(ValueError):
            self.f.act('message', sender=other, reply_to=source['id'], text='Blocked')
        before = self.f.hub.snapshot()
        with self.assertRaises(ValueError):
            self.f.act('message', reply_to='other-room-message', text='Invalid')
        self.assertEqual(before, self.f.hub.snapshot())

    def test_selected_code_followup_delivers_previous_answer_only_after_new_approval(self):
        result = self.diff(path='app.py')
        first = self.query(result, selection={'new': [2, 2]}, question='Explain the new return')['job_id']
        self.f.act('approve', job_id=first)
        self.assertEqual(self.f.wait(first)['status'], 'finished')
        second = self.query(result, reply_to=first, question='Follow-up about the old return', selection={'old': [2, 2]},
                            history=['CLIENT HISTORY MUST NOT BE USED'])['job_id']
        job = self.f.hub.room(self.f.rid)['jobs'][second]
        self.assertEqual(job['status'], 'pending')
        self.assertFalse(self.f.hub.processes)
        self.assertEqual(job['diff_context']['thread_id'], first)
        self.assertEqual(job['diff_context']['selection'], {'old': [2, 2]})
        self.assertEqual(job['diff_context']['history_job_ids'], [first])
        self.assertIn('FIXTURE CHECKED', ''.join(job['references']))
        self.assertNotIn('CLIENT HISTORY', ''.join(job['references']))
        self.assertNotIn('FIXTURE CHECKED', job['prompt'])
        self.assertEqual(json.loads(job['references'][-1])['earlier_turns'][0]['selection'], {'new': [2, 2]})
        self.assertIn('FIXTURE CHECKED', ''.join(self.f.hub.approval_details(self.f.rid, second)['references']))
        public = json.dumps(self.f.hub.board()) + json.dumps(self.f.hub.run_status(self.f.rid, second))
        self.assertNotIn('Explain the new return', public)
        self.assertNotIn('FIXTURE CHECKED', public)
        self.f.hub.config['drivers']['read']['argv'] = [os.sys.executable, '-c',
            'import sys; value=sys.stdin.read(); print("HISTORY DELIVERED" if "FIXTURE CHECKED" in value and "Follow-up about the old return" in value else "MISSING")']
        self.f.act('approve', job_id=second)
        self.assertEqual(self.f.wait(second)['status'], 'finished')
        self.assertIn('HISTORY DELIVERED', job['output'])

    def test_followup_rejects_wrong_scope_and_unfinished_answers_atomically(self):
        result = self.diff(path='app.py')
        first = self.query(result)['job_id']
        before = self.f.hub.snapshot()
        for parent in ('missing', [], first):
            with self.assertRaises(ValueError):
                self.query(result, reply_to=parent)
            self.assertEqual(before, self.f.hub.snapshot())
        self.f.act('approve', job_id=first)
        self.f.wait(first)
        other = self.f.act('add_member', name='Other reviewer', project='product')['member_id']
        other_room = self.f.hub.action({'action': 'create_room', 'title': 'Other', 'goal': 'Synthetic'})['room_id']
        elsewhere = self.f.hub.action({'action': 'request_run', 'room_id': other_room,
            'member_id': self.f.hub.action({'action': 'add_member', 'room_id': other_room,
                'name': 'Other', 'project': 'product'})['member_id'], 'driver': 'read', 'prompt': 'Other'})['job_id']
        general = self.f.request()
        for changed, overrides in ((result, {'reply_to': elsewhere}), (result, {'reply_to': general}),
                (result, {'reply_to': first, 'member_id': other}), (result, {'reply_to': first, 'driver': 'slow'}),
                (self.diff(path='new file.txt'), {'reply_to': first})):
            before = self.f.hub.snapshot()
            with self.assertRaises(ValueError):
                self.query(changed, **overrides)
            self.assertEqual(before, self.f.hub.snapshot())
        self.write('app.py', 'def greet():\n    return "later"\n')
        before = self.f.hub.snapshot()
        with self.assertRaises(ValueError):
            self.query(self.diff(path='app.py'), reply_to=first)
        self.assertEqual(before, self.f.hub.snapshot())

    def test_code_history_keeps_recent_three_turns_with_visible_limits(self):
        result = self.diff(path='app.py')
        self.f.hub.config['drivers']['read']['argv'] = [os.sys.executable, '-c',
            'import sys; sys.stdin.read(); print("SYNTHETIC ANSWER " + "a" * 1000)']
        ids = []
        for index in range(5):
            jid = self.query(result, reply_to=ids[-1] if ids else None, question=f'Turn {index}')['job_id']
            self.f.act('approve', job_id=jid)
            self.assertEqual(self.f.wait(jid)['status'], 'finished')
            ids.append(jid)
        job = self.f.hub.room(self.f.rid)['jobs'][ids[-1]]
        self.assertEqual(job['diff_context']['thread_id'], ids[0])
        self.assertEqual(job['diff_context']['history_job_ids'], ids[1:4])
        self.assertTrue(job['diff_context']['history_truncated'])
        self.assertTrue(job['diff_context']['older_turns_omitted'])
        self.assertLessEqual(sum(map(len, job['references'])), 16000)
        self.assertTrue(all(len(ref) <= 4000 for ref in job['references']))
        self.assertEqual(len(job['references']), len(gitdiff.question_references(result)) + 1)
        history = json.loads(job['references'][-1])
        self.assertEqual([turn['question'] for turn in history['earlier_turns']], ['Turn 1', 'Turn 2', 'Turn 3'])
        self.assertTrue(all(turn['truncated'] for turn in history['earlier_turns']))

    def test_owner_http_only_and_no_automatic_model_call(self):
        with http_server(self.f) as server:
            url = '/api/diff?' + urlencode({'room_id': self.f.rid, 'project': 'product', 'path': 'app.py'})
            code, result, _ = http(server, url)
            self.assertEqual(code, 200)
            self.assertEqual(http(server, url, viewer=True)[0], 403)
            data = {'room_id': self.f.rid, 'project': 'product', 'path': result['path'], 'digest': result['digest'],
                    'base': result['base'], 'driver': 'read', 'member_id': self.f.mid, 'question': 'Explain'}
            self.assertEqual(http(server, '/api/diff/question', data, viewer=True)[0], 403)
            accepted, body, _ = http(server, '/api/diff/question', data)
            self.assertEqual(accepted, 202)
            self.assertEqual(self.f.hub.run_status(self.f.rid, body['job_id'])['status'], 'pending')
            self.assertFalse(self.f.hub.processes)
            connection = HTTPConnection('127.0.0.1', server.server_port, timeout=5)
            connection.request('GET', '/compare.js')
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertIn(b'RoomCompare', response.read())
            connection.close()


if __name__ == '__main__':
    unittest.main()
