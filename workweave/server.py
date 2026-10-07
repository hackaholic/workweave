"""WorkWeave HTTP Server: Serves live workflow dashboard and JSON APIs."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from workweave.dashboard import generate_html_dashboard
from workweave.parser import parse_work_directory

logger = logging.getLogger("workweave.server")


def create_handler_class(target_path: Path | str, project_title: str | None = None):
    """Create a configured BaseHTTPRequestHandler class."""

    class WorkWeaveHandler(BaseHTTPRequestHandler):
        server_version = "WorkWeave/1.0"

        def do_GET(self) -> None:  # noqa: N802
            parsed_path = urlparse(self.path).path

            if parsed_path in ("/", "/index.html"):
                try:
                    state = parse_work_directory(target_path, project_title=project_title)
                    html_content = generate_html_dashboard(state)
                    body = html_content.encode("utf-8")
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.end_headers()
                    self.wfile.write(body)
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Failed to render dashboard")
                    self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"Dashboard render error: {exc}")

            elif parsed_path in ("/api/workflow", "/api/state"):
                try:
                    state = parse_work_directory(target_path, project_title=project_title)
                    json_data = json.dumps(asdict(state), indent=2)
                    body = json_data.encode("utf-8")
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.end_headers()
                    self.wfile.write(body)
                except Exception as exc:  # noqa: BLE001
                    logger.exception("Failed to render state JSON")
                    self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, f"API error: {exc}")

            elif parsed_path == "/health":
                health_payload = json.dumps({"status": "ok", "service": "workweave"}).encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(health_payload)))
                self.end_headers()
                self.wfile.write(health_payload)

            else:
                self.send_error(HTTPStatus.NOT_FOUND, f"Path not found: {parsed_path}")

        def log_message(self, format: str, *args) -> None:  # noqa: A002
            logger.info("%s - %s", self.address_string(), format % args)

    return WorkWeaveHandler


class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


def run_server(
    host: str = "0.0.0.0",
    port: int = 8088,
    target_path: Path | str = ".",
    project_title: str | None = None,
) -> None:
    """Start WorkWeave HTTP server."""
    handler_class = create_handler_class(target_path, project_title)
    server = ReusableHTTPServer((host, port), handler_class)
    print(f"==================================================")
    print(f"  WorkWeave Dashboard Server")
    print(f"  Target: {Path(target_path).resolve()}")
    print(f"  Listening on: http://{host}:{port}")
    print(f"==================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping WorkWeave server...")
    finally:
        server.server_close()
