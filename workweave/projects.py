"""Persistent local project registry; monitored directories are never modified."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import uuid
from pathlib import Path

from workweave.parser import resolve_work_directory


class ProjectError(ValueError):
    def __init__(self, message: str, status: int = 400, code: str = "invalid_project"):
        super().__init__(message)
        self.status = status
        self.code = code


class ProjectRegistry:
    """One server process per registry. Writes within that process are serialized."""

    def __init__(self, data_dir: Path | str, projects_root: Path | str | None = None):
        self.path = Path(data_dir).expanduser().resolve() / "projects.json"
        self.root = Path(projects_root).expanduser().resolve() if projects_root else None
        self.lock = threading.RLock()

    def list(self) -> list[dict[str, str]]:
        with self.lock:
            if not self.path.exists():
                return []
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if not isinstance(data, dict) or data.get("version") != 1:
                    raise ValueError
                projects = data["projects"]
                if not isinstance(projects, list):
                    raise ValueError
                ids, paths = set(), set()
                for project in projects:
                    if not isinstance(project, dict) or set(project) != {"id", "name", "path"}:
                        raise ValueError
                    if not all(isinstance(v, str) and v for v in project.values()):
                        raise ValueError
                    if uuid.UUID(project["id"]).hex != project["id"]:
                        raise ValueError
                    if not Path(project["path"]).is_absolute():
                        raise ValueError
                    if project["id"] in ids or project["path"] in paths:
                        raise ValueError
                    ids.add(project["id"])
                    paths.add(project["path"])
                return projects
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise ProjectError("Cannot read the project registry. Check projects.json in the data directory; it has not been overwritten.", 500, "registry_unavailable") from exc

    def resolve(self, raw_path: str) -> tuple[Path, Path]:
        if not isinstance(raw_path, str) or not raw_path.strip() or len(raw_path) > 4096 or "\x00" in raw_path:
            raise ProjectError("Enter an absolute project folder path.")
        path = Path(raw_path.strip()).expanduser()
        if not path.is_absolute():
            raise ProjectError("Use an absolute folder path visible to WorkWeave.")
        try:
            path = path.resolve()
            self._check_root(path)
            if not path.is_dir():
                raise ProjectError("Project folder is missing or unavailable. Check the path and folder permissions.")
            work_dir, project_root = resolve_work_directory(path)
            self._check_root(work_dir.resolve())
            if not (work_dir.name == "work" or (work_dir / "INDEX.md").is_file()
                    or any(p.is_dir() and p.name.startswith("work-") for p in work_dir.iterdir())):
                raise ProjectError("Choose a project containing a work/ folder, or a workflow folder with INDEX.md or work-* folders.")
            # Enumerate now so inaccessible directories fail at registration.
            list(work_dir.iterdir())
            return work_dir.resolve(), project_root
        except (OSError, RuntimeError) as exc:
            raise ProjectError("Cannot read this folder. Check the path and folder permissions.") from exc

    def _check_root(self, path: Path) -> None:
        if self.root is not None and path != self.root and self.root not in path.parents:
            raise ProjectError(f"Choose a folder inside {self.root}.", 400, "outside_projects_root")

    def browse(self, raw_path: str | None = None) -> dict:
        """List directories only, without changing the registry or project files."""
        start = self.root or Path.home().resolve()
        if raw_path is None:
            path = start
        else:
            if not isinstance(raw_path, str) or not raw_path or len(raw_path) > 4096 or "\x00" in raw_path:
                raise ProjectError("Choose a valid absolute folder path.")
            path = Path(raw_path).expanduser()
            if not path.is_absolute():
                raise ProjectError("Choose an absolute folder path.")
        try:
            path = path.resolve()
            self._check_root(path)
            if not path.is_dir():
                raise ProjectError("Folder is missing or unavailable.", 404, "folder_unavailable")
            directories = []
            for child in path.iterdir():
                try:
                    if not child.is_dir():
                        continue
                    resolved = child.resolve()
                    self._check_root(resolved)
                    directories.append({"name": child.name, "path": str(resolved)})
                except (OSError, RuntimeError, ProjectError):
                    # Broken links and links outside the configured root are not navigation targets.
                    continue
            directories.sort(key=lambda entry: (entry["name"].casefold(), entry["name"]))
            try:
                self.resolve(str(path))
                selectable, reason = True, "Ready to add as a project."
            except ProjectError as exc:
                selectable, reason = False, str(exc)
            parent = None if path == self.root or path.parent == path else str(path.parent)
            return {"path": str(path), "parent": parent, "start": str(start),
                    "directories": directories[:1000], "truncated": len(directories) > 1000,
                    "selectable": selectable, "reason": reason}
        except (OSError, RuntimeError) as exc:
            raise ProjectError("Cannot browse this folder. Check folder permissions or choose another folder.", 403, "folder_unreadable") from exc

    def add(self, path: str, name: str = "") -> dict[str, str]:
        if not isinstance(name, str) or len(name.strip()) > 120:
            raise ProjectError("Project name must be text with at most 120 characters.")
        work_dir, root = self.resolve(path)
        with self.lock:
            projects = self.list()
            if any(p["path"] == str(work_dir) for p in projects):
                raise ProjectError("This project has already been added.", 409, "duplicate_project")
            project = {"id": uuid.uuid4().hex, "name": name.strip() or root.name.replace("-", " ").replace("_", " ").title() or "Project", "path": str(work_dir)}
            projects.append(project)
            temp_path = None
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent, delete=False) as handle:
                    temp_path = Path(handle.name)
                    json.dump({"version": 1, "projects": projects}, handle, indent=2)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temp_path, self.path)
            except OSError as exc:
                raise ProjectError("Cannot save projects. Check data-directory permissions.", 500, "registry_unavailable") from exc
            finally:
                if temp_path is not None:
                    temp_path.unlink(missing_ok=True)
            return project

    def get(self, project_id: str) -> dict[str, str]:
        for project in self.list():
            if project["id"] == project_id:
                return project
        raise ProjectError("Project not found. Return to Projects to select one.", 404, "project_not_found")
