import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from workweave.server import ReusableHTTPServer, create_handler_class


class TestProjectAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / 'data'
        self.server = ReusableHTTPServer(('127.0.0.1', 0), create_handler_class(data_dir=self.data, projects_root=self.root))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, method, path, payload=None, headers=None, raw=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        self.addCleanup(conn.close)
        body = raw if raw is not None else json.dumps(payload) if payload is not None else None
        req_headers = {'Content-Type': 'application/json', 'X-WorkWeave-Request': '1'}
        req_headers.update(headers or {})
        conn.request(method, path, body, req_headers)
        res = conn.getresponse()
        content = res.read().decode()
        return res.status, json.loads(content) if res.getheader('Content-Type', '').startswith('application/json') else content

    def add(self, name):
        work = self.root / name / 'work'
        work.mkdir(parents=True)
        item = work / 'work-001'
        item.mkdir()
        (item / 'README.md').write_text('## Goal\n' + name + ' objective')
        status, data = self.request('POST', '/api/projects', {'path': str(work.parent), 'name': name})
        self.assertEqual(status, 201)
        return data['project']

    def test_empty_onboarding_and_navigation(self):
        self.assertEqual(self.request('GET', '/api/projects'), (200, {'projects': []}))
        status, page = self.request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn('No projects yet', page)
        first, second = self.add('Alpha'), self.add('Beta')
        for project in [first, second]:
            status, data = self.request('GET', '/api/projects/' + project['id'] + '/workflow')
            self.assertEqual(status, 200)
            self.assertEqual(data['project_name'], project['name'])
            self.assertEqual(data['items'][0]['goal'], project['name'] + ' objective')
            status, page = self.request('GET', '/projects/' + project['id'])
            self.assertEqual(status, 200)
            self.assertIn('Project navigation', page)
            self.assertIn('All projects / Add project', page)
        self.assertEqual(self.request('GET', '/api/workflow')[0], 400)
        self.assertEqual(self.request('GET', '/api/state?project=' + second['id'])[1]['project_name'], 'Beta')
        self.assertEqual(self.request('GET', '/api/projects/unknown/workflow')[0], 404)

    def test_missing_directory_and_hostile_title(self):
        project = self.add('Alpha')
        registry_path = self.data / 'projects.json'
        registry = json.loads(registry_path.read_text())
        registry['projects'][0]['name'] = '</script><script>alert(1)</script>'
        registry_path.write_text(json.dumps(registry))
        _, page = self.request('GET', '/projects/' + project['id'])
        self.assertNotIn('</script><script>alert(1)</script>', page)
        self.assertIn('\\u003c/script>', page)
        Path(project['path']).rename(self.root / 'moved')
        status, page = self.request('GET', '/projects/' + project['id'])
        self.assertEqual(status, 409)
        self.assertIn('Return to Projects', page)
        self.assertEqual(len(self.request('GET', '/api/projects')[1]['projects']), 1)

    def test_rejections_have_no_side_effects(self):
        work = self.root / 'alpha' / 'work'
        work.mkdir(parents=True)
        payload = {'path': str(work)}
        cases = [({'Origin': 'http://evil.example'}, 403),
                 ({'Host': 'evil.example'}, 403),
                 ({'Sec-Fetch-Site': 'cross-site'}, 403),
                 ({'X-WorkWeave-Request': ''}, 403),
                 ({'Content-Type': 'text/plain'}, 415)]
        for headers, expected in cases:
            with self.subTest(headers=headers):
                self.assertEqual(self.request('POST', '/api/projects', payload, headers)[0], expected)
        for payload in [[], {}, {'path': 3}, {'path': str(work), 'extra': True}, {'path': str(work), 'name': []}]:
            self.assertEqual(self.request('POST', '/api/projects', payload)[0], 400)
        self.assertEqual(self.request('POST', '/api/projects', raw='{broken')[0], 400)
        self.assertEqual(self.request('POST', '/api/projects', raw='x' * 17000)[0], 413)
        self.assertFalse(self.data.exists())
        self.assertEqual(self.request('GET', '/api/projects', headers={'Host':'evil.example'})[0], 403)

    def test_duplicate_and_corrupt_registry(self):
        project = self.add('Alpha')
        self.assertEqual(self.request('POST', '/api/projects', {'path': project['path']})[0], 409)
        path = self.data / 'projects.json'
        path.write_text('invalid')
        status, data = self.request('GET', '/api/projects')
        self.assertEqual(status, 500)
        self.assertEqual(data['error']['code'], 'registry_unavailable')
        self.assertEqual(path.read_text(), 'invalid')

    def test_folder_api(self):
        from urllib.parse import quote
        project = self.root / 'A & B'
        (project / 'work').mkdir(parents=True)
        status, data = self.request('GET', '/api/folders')
        self.assertEqual(status, 200)
        self.assertIsNone(data['parent'])
        self.assertEqual(data['directories'], [{'name': 'A & B', 'path': str(project)}])
        status, data = self.request('GET', '/api/folders?path=' + quote(str(project)))
        self.assertEqual(status, 200)
        self.assertTrue(data['selectable'])
        self.assertEqual(self.request('GET', '/api/folders?path=' + quote(str(self.root.parent)))[0], 400)
        for headers in [{'Host': 'evil.example'}, {'Origin': 'http://evil.example'}]:
            status, data = self.request('GET', '/api/folders', headers=headers)
            self.assertEqual(status, 403)
            self.assertNotIn('directories', data)
        self.assertFalse(self.data.exists())
