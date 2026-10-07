"""Unit tests for WorkWeave HTTP server."""

import json
import socket
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

from workweave.server import ReusableHTTPServer, create_handler_class


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.work_dir = Path(cls.temp_dir.name) / "work"
        cls.work_dir.mkdir()

        (cls.work_dir / "INDEX.md").write_text(
            "- **Work 001 — Alpha** · Completed · [work folder](work-001/)\n",
            encoding="utf-8",
        )
        w1 = cls.work_dir / "work-001"
        w1.mkdir()
        (w1 / "README.md").write_text("## Goal\nAlpha release", encoding="utf-8")
        (w1 / "tasks.md").write_text("- [x] 1.1 First task\n", encoding="utf-8")

        cls.port = find_free_port()
        handler_class = create_handler_class(cls.temp_dir.name, project_title="Test App", data_dir=Path(cls.temp_dir.name) / "data")
        cls.server = ReusableHTTPServer(("127.0.0.1", cls.port), handler_class)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp_dir.cleanup()

    def test_health_endpoint(self):
        url = f"http://127.0.0.1:{self.port}/health"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(data["status"], "ok")
            self.assertEqual(data["service"], "workweave")

    def test_workflow_api(self):
        url = f"http://127.0.0.1:{self.port}/api/workflow"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertEqual(data["project_name"], "Test App")
            self.assertEqual(data["total_work_items"], 1)
            self.assertEqual(data["completed_items"], 1)

    def test_dashboard_html(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/projects") as response:
            project_id = json.load(response)["projects"][0]["id"]
        url = f"http://127.0.0.1:{self.port}/projects/{project_id}"
        with urllib.request.urlopen(url) as response:
            self.assertEqual(response.status, 200)
            html = response.read().decode("utf-8")
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("Test App", html)
            self.assertIn("WorkWeave", html)

    def test_not_found(self):
        url = f"http://127.0.0.1:{self.port}/nonexistent"
        try:
            urllib.request.urlopen(url)
            self.fail("Expected HTTPError 404")
        except urllib.error.HTTPError as err:
            self.assertEqual(err.code, 404)

    def test_post_mutation_apis(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir) / "work"
            work_dir.mkdir()
            (work_dir / "INDEX.md").write_text(
                "- **Work 001 — Alpha** · Completed · [work folder](work-001/)\n",
                encoding="utf-8",
            )
            w1 = work_dir / "work-001"
            w1.mkdir()
            (w1 / "README.md").write_text("## Goal\nAlpha release", encoding="utf-8")
            (w1 / "tasks.md").write_text("- [x] 1.1 First task\n", encoding="utf-8")

            port = find_free_port()
            handler_class = create_handler_class(tmpdir, project_title="Mutation App", data_dir=Path(tmpdir) / "data")
            server = ReusableHTTPServer(("127.0.0.1", port), handler_class)
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            try:
                # 1. Post comment
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/comments",
                    data=json.dumps({"work_id": "work-001", "text": "Server test comment", "author": "Bot"}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "X-WorkWeave-Request": "1"},
                )
                with urllib.request.urlopen(req) as response:
                    self.assertEqual(response.status, 201)
                    data = json.loads(response.read().decode("utf-8"))
                    self.assertEqual(data["status"], "ok")
                    self.assertEqual(data["comment"]["author"], "Bot")

                # 2. Toggle subtask
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/subtasks/toggle",
                    data=json.dumps({"work_id": "work-001", "subtask_id": "1-1-first-task", "completed": False}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "X-WorkWeave-Request": "1"},
                )
                with urllib.request.urlopen(req) as response:
                    self.assertEqual(response.status, 200)

                # 3. Create draft work
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/work/new",
                    data=json.dumps({"title": "API Created Work", "description": "From test", "is_draft": True}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "X-WorkWeave-Request": "1"},
                )
                with urllib.request.urlopen(req) as response:
                    self.assertEqual(response.status, 201)
                    data = json.loads(response.read().decode("utf-8"))
                    self.assertEqual(data["status"], "ok")
                    self.assertTrue(data["folder_name"].startswith("work-002-"))
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
