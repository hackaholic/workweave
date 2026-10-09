"""WorkWeave HTTP server for a local project library and workflow dashboards."""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from workweave.views.review import render_review
from workweave.controllers import lifecycle as lifecycle_controller
from workweave.schemas.lifecycle import LifecycleError
from workweave.repositories.lifecycle import find_work, safe_file
from workweave.services import lifecycle

from workweave.dashboard import generate_html_dashboard
from workweave.parser import (
    add_work_comment,
    create_subtask,
    create_work_item,
    parse_work_directory,
    scaffold_draft_work,
    update_subtask,
)
from workweave.project_ui import project_error, project_library, project_navigation
from workweave.projects import ProjectError, ProjectRegistry

logger = logging.getLogger("workweave.server")


def default_data_dir() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))) / "workweave"


def create_handler_class(
    target_path: Path | str | None = None,
    project_title: str | None = None,
    data_dir: Path | str | None = None,
    projects_root: Path | str | None = None,
):
    """Create a handler with a persistent registry; an explicit target seeds it."""
    registry = ProjectRegistry(data_dir if data_dir is not None else default_data_dir(), projects_root)
    if target_path is not None:
        try:
            registry.add(str(Path(target_path).resolve()), project_title or "")
        except ProjectError as exc:
            if exc.code != "duplicate_project":
                raise

    class WorkWeaveHandler(BaseHTTPRequestHandler):
        server_version = "WorkWeave/1.0"

        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def respond(self, status, data, content_type="application/json; charset=utf-8"):
            body = (json.dumps(data) if content_type.startswith("application/json") else data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.end_headers()
            self.wfile.write(body)

        def error(self, exc, html=False):
            if html:
                self.respond(exc.status, project_error(str(exc)), "text/html; charset=utf-8")
            else:
                self.respond(exc.status, {"error": {"code": exc.code, "message": str(exc)}})

        def validate_request_origin(self):
            host = self.headers.get("Host", "")
            try:
                hostname = urlparse("http://" + host).hostname
            except ValueError:
                hostname = None
            allowed = {"localhost", "127.0.0.1", "::1", self.server.server_address[0]}
            allowed.discard("0.0.0.0")
            if hostname not in allowed:
                raise ProjectError("Use the local WorkWeave address.", 403, "invalid_host")
            origin = self.headers.get("Origin")
            if (origin and origin != "http://" + host) or self.headers.get("Sec-Fetch-Site") == "cross-site":
                raise ProjectError("Cross-origin requests are not allowed.", 403, "invalid_origin")

        def workflow(self, project_id):
            project = registry.get(project_id)
            try:
                work_dir, _ = registry.resolve(project["path"])
                state = parse_work_directory(work_dir, project_title=project["name"])
            except (ProjectError, OSError, RuntimeError) as exc:
                raise ProjectError("This project's workflow folder is unavailable. Check its location, permissions, or Docker mount, then retry.", 409, "project_unavailable") from exc
            return state

        def do_GET(self):  # noqa: N802
            parsed = urlparse(self.path)
            route = parsed.path
            html = route.startswith("/projects/")
            try:
                self.validate_request_origin()
                if route in ("/", "/index.html"):
                    self.respond(200, project_library(registry.root), "text/html; charset=utf-8")
                elif route == "/api/lifecycle":
                    query = parse_qs(parsed.query)
                    self.respond(200, lifecycle_controller.get(registry, query.get("project", [None])[0], query.get("work", [None])[0]))
                elif route == "/api/projects":
                    self.respond(200, {"projects": registry.list()})
                elif route == "/api/folders":
                    query = parse_qs(parsed.query, keep_blank_values=True)
                    self.respond(200, registry.browse(query.get("path", [None])[0]))
                elif re.fullmatch(r'/projects/[a-f0-9]{32}/work/work-\d+/review', route):
                    parts = route.split('/')
                    find_work(lifecycle_controller.selected_project(registry, parts[2]), parts[4])
                    self.respond(200, render_review(parts[2], parts[4]), "text/html; charset=utf-8")
                elif route.startswith("/projects/"):
                    project_id = route.removeprefix("/projects/")
                    state = self.workflow(project_id)
                    nav = project_navigation(registry.list(), project_id)
                    self.respond(200, generate_html_dashboard(state, navigation=nav, project_id=project_id), "text/html; charset=utf-8")
                elif route.startswith("/api/projects/") and route.endswith("/workflow"):
                    project_id = route[len("/api/projects/"):-len("/workflow")]
                    self.respond(200, asdict(self.workflow(project_id)))
                elif route in ("/api/workflow", "/api/state"):
                    project_id = parse_qs(parsed.query).get("project", [None])[0]
                    if not project_id:
                        projects = registry.list()
                        if len(projects) != 1:
                            raise ProjectError("Select a project using ?project=<id>.", 400, "project_required")
                        project_id = projects[0]["id"]
                    self.respond(200, asdict(self.workflow(project_id)))
                elif route == "/health":
                    self.respond(200, {"status": "ok", "service": "workweave"})
                else:
                    raise ProjectError("Path not found.", 404, "not_found")
            except (ProjectError, LifecycleError) as exc:
                self.error(exc, html)
            except Exception:
                logger.exception("Failed to serve request")
                self.error(ProjectError("Unable to load this page. Check the server logs.", 500, "internal_error"), html)

        def do_POST(self):  # noqa: N802
            try:
                self.validate_request_origin()
                path = urlparse(self.path).path
                valid_post_paths = {
                    "/api/projects",
                    "/api/lifecycle",
                    "/api/comments",
                    "/api/subtasks/toggle",
                    "/api/subtasks/new",
                    "/api/work/new",
                    "/api/work/scaffold",
                }
                if path not in valid_post_paths:
                    raise ProjectError("Path not found.", 404, "not_found")
                if self.headers.get_content_type() != "application/json":
                    raise ProjectError("Send application/json.", 415, "invalid_content_type")
                if self.headers.get("X-WorkWeave-Request") != "1":
                    raise ProjectError("Missing WorkWeave request header.", 403, "invalid_request")
                if self.headers.get("Transfer-Encoding"):
                    raise ProjectError("Transfer encoding is not supported.")
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    raise ProjectError("Invalid content length.") from None
                if length <= 0 or length > 16384:
                    raise ProjectError("Request body must be between 1 and 16384 bytes.", 413, "invalid_size")
                try:
                    payload = json.loads(self.rfile.read(length))
                except (ValueError, UnicodeError):
                    raise ProjectError("Invalid JSON body.") from None
                if not isinstance(payload, dict):
                    raise ProjectError("Request body must be a JSON object.")

                if path == "/api/lifecycle":
                    self.respond(200, lifecycle_controller.post(registry, payload))
                    return

                if path == "/api/projects":
                    if set(payload) - {"path", "name"}:
                        raise ProjectError("Expected path and optional name fields.")
                    project = registry.add(payload.get("path"), payload.get("name", ""))
                    self.respond(201, {"project": project})
                    return

                # Target directory resolution for work-level mutations
                project_id = payload.get("project_id")
                if project_id:
                    project = registry.get(project_id)
                    work_target = project["path"]
                else:
                    projects = registry.list()
                    if len(projects) == 1:
                        work_target = projects[0]["path"]
                    else:
                        raise ProjectError("Project ID is required.", 400, "project_required")

                # Revalidate project mount and all work-local write targets.
                work_target, _ = registry.resolve(work_target)
                for key in ('work_id', 'subtask_id', 'title', 'text', 'author', 'owner', 'description'):
                    if key in payload and not isinstance(payload[key], str):
                        raise LifecycleError(f'{key} must be text.')
                if path != '/api/work/new':
                    folder = find_work(work_target, payload.get('work_id'))
                    for filename in ('README.md', 'tasks.md', 'comments.md', 'notes.md', 'coordination.md', 'decisions.md', 'tasks'):
                        safe_file(folder, filename)
                if path == '/api/subtasks/toggle' and payload.get('title') is None:
                    task_id = payload.get('subtask_id', '')
                    if not task_id.startswith('planned-'):
                        raise LifecycleError('Only approved plan tasks can be executed. Use Plan & review.', 'review_required', 409)
                    data = lifecycle.toggle_task(folder, task_id[len('planned-'):], payload.get('completed'), payload.get('expected_version'))
                    self.respond(200, {'status': 'ok', 'updated': True, 'lifecycle': data})
                    return
                if path in ('/api/subtasks/new', '/api/subtasks/toggle'):
                    data = lifecycle.state(folder)
                    if data.get('managed') and data['phase'] != 'Draft':
                        raise LifecycleError('Task definition changes require Request changes and a new reviewed plan.', 'review_required', 409)
                    if payload.get('completed') is not None:
                        raise LifecycleError('Planning edits cannot also change completion.', 'review_required', 409)
                    if payload.get('subtask_id', '').startswith('planned-'):
                        raise LifecycleError('Revise planned task definitions in the next plan return.', 'review_required', 409)

                if path == "/api/comments":
                    work_id = payload.get("work_id", "").strip()
                    comment_text = payload.get("text", "").strip()
                    author = payload.get("author", "User").strip() or "User"
                    subtask_id = payload.get("subtask_id", "").strip()
                    if not work_id or not comment_text:
                        raise ProjectError("work_id and text are required fields.")
                    comment = add_work_comment(work_target, work_id, comment_text, author=author, subtask_id=subtask_id)
                    self.respond(201, {"status": "ok", "comment": asdict(comment)})

                elif path == "/api/subtasks/toggle":
                    work_id = payload.get("work_id", "").strip()
                    subtask_id = payload.get("subtask_id", "").strip()
                    new_title = payload.get("title")
                    completed = payload.get("completed")
                    if not work_id or not subtask_id:
                        raise ProjectError("work_id and subtask_id are required fields.")
                    ok = update_subtask(work_target, work_id, subtask_id, new_title=new_title, completed=completed)
                    self.respond(200, {"status": "ok", "updated": ok})

                elif path == "/api/subtasks/new":
                    work_id = payload.get("work_id", "").strip()
                    title = payload.get("title", "").strip()
                    owner = payload.get("owner", "").strip()
                    if not work_id or not title:
                        raise ProjectError("work_id and title are required fields.")
                    subtask = create_subtask(work_target, work_id, title, owner=owner)
                    self.respond(201, {"status": "ok", "subtask": asdict(subtask)})

                elif path == "/api/work/new":
                    title = payload.get("title", "").strip()
                    description = payload.get("description", "")
                    is_draft = payload.get("is_draft", True)
                    owner = payload.get("owner", "Unassigned").strip() or "Unassigned"
                    if not title:
                        raise ProjectError("Work item title is required.")
                    folder_name = create_work_item(work_target, title, description=description, is_draft=is_draft, owner=owner)
                    self.respond(201, {"status": "ok", "folder_name": folder_name})

                elif path == "/api/work/scaffold":
                    work_id = payload.get("work_id", "").strip()
                    if not work_id:
                        raise ProjectError("work_id is required.")
                    ok = scaffold_draft_work(work_target, work_id)
                    self.respond(200, {"status": "ok", "scaffolded": ok})

            except (ProjectError, LifecycleError) as exc:
                self.error(exc)
            except Exception:
                logger.exception("Failed to process request")
                self.error(ProjectError("Unable to process request. Check the server logs.", 500, "internal_error"))

        def log_message(self, format, *args):  # noqa: A002
            logger.info("%s - %s", self.address_string(), format % args)

    return WorkWeaveHandler


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


def run_server(
    host: str = "127.0.0.1",
    port: int = 8088,
    target_path: Path | str | None = None,
    project_title: str | None = None,
    data_dir: Path | str | None = None,
    projects_root: Path | str | None = None,
) -> None:
    """Start WorkWeave; local use only, with no remote authentication."""
    handler_class = create_handler_class(target_path, project_title, data_dir, projects_root)
    server = ReusableHTTPServer((host, port), handler_class)
    print(f"WorkWeave projects: http://{host}:{port}")
    print(f"Registry: {Path(data_dir) if data_dir is not None else default_data_dir()}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping WorkWeave server...")
    finally:
        server.server_close()
