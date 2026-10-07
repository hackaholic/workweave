# WorkWeave 🧶

**WorkWeave** is a lightweight, zero-dependency multi-agent workflow and task coordination dashboard. It parses and visualizes structured project work directories, rescanning when you load or refresh a dashboard.

---

## ✨ Features

- **Multiple Local Projects:** Add projects from the browser, retain them across restarts, and switch between their dashboards.
- **Zero Runtime Dependencies:** Pure Python standard library (no pip packages needed to run).
- **Universal Target Resolution:** Point to any repository root with a `work/` folder, or point directly to a `work/` folder.
- **Interactive Dashboard:** Modern Tailwind CSS UI with KPI summary, progress bars, search/filter pills, subtask checklist, and interactive contract inspector modals.
- **Dynamic Project Branding:** Automatically infers project titles and adapts seamlessly to any codebase.
- **REST APIs Built-in:**
  - `GET /` — Project library and onboarding
  - `GET /projects/<id>` — Selected project dashboard
  - `GET /api/projects` — Saved projects
  - `POST /api/projects` — Register a project
  - `GET /api/folders?path=<absolute path>` — Browse folders (omit path for the starting folder)
  - `GET /api/projects/<id>/workflow` — Selected project state
  - `GET /api/workflow` / `GET /api/state` — State for `?project=<id>`, or the sole registered project
  - `GET /health` — Health check endpoint
- **Docker-Ready:** Minimal Alpine Linux image with non-root security and healthcheck.

---

## 🚀 Quickstart

### 1. Run Locally (Python)

```bash
# Start with an empty project library (on first run)
python -m workweave.cli

# Optionally register a project on startup
python -m workweave.cli --target /path/to/project

# Change port and project title
python -m workweave.cli --target /path/to/project --port 8088 --title "My Cool Project"

# Export static HTML snapshot
python -m workweave.cli --target /path/to/project --build ./dashboard.html

# Output JSON to stdout
python -m workweave.cli --target /path/to/project --json
```

### 2. Run with Docker Compose

Start the app, then open [WorkWeave](http://localhost:8088). Compose mounts the parent of this checkout by default, so sibling repositories are available under `/projects`:

```bash
docker compose up -d --build
# In the UI, add /projects/my-project (or /projects/my-project/work).
```

To use a different parent folder, configure it once:

```bash
PROJECTS_PATH=/absolute/path/to/repos docker compose up -d --build
```

Add any project beneath that parent through the UI; no per-project Compose edits are needed. Docker cannot see arbitrary host folders: `/home/you/repos/example` on the host becomes `/projects/example` when `/home/you/repos` is mounted. Folders outside the mounted parent require a different mount or running WorkWeave natively. The container's non-root user needs read/traverse permission on monitored folders.

The `workweave-data` named volume stores registrations at `/data/projects.json`. Project folders are mounted read-only. Rebuilding or restarting preserves registrations; `docker compose down -v` removes that volume. The published port binds only to `127.0.0.1`.

If your installation provides the standalone command, use `docker-compose` in place of `docker compose`.

### Adding and navigating projects

1. In **Add a project**, click **Browse…**, open the desired folder, and click **Select this folder**. Then optionally set a display name and click **Add project**. You can also enter a path manually.
   The browser lists folders only, with **Up one level** and **Starting folder** controls. Selection is enabled when the current folder contains a valid workflow. Cancel or Escape leaves the form unchanged. Docker browsing starts at `/projects` and stays within that mount; native browsing starts at your home directory. Nothing is uploaded or modified by browsing. Listings are limited to 1000 folders; use an exact path for folders beyond that limit.
2. A valid target contains a `work/` directory, or is itself a workflow directory named `work`, containing `INDEX.md`, or containing `work-*` folders. An empty `work/` directory is supported.
3. Adding opens its dashboard. Use the **Project** dropdown to switch, or **All projects / Add project** to return to the library.
4. Use **Sync** to rescan a selected project. The UI does not poll for changes automatically.

Registration never modifies the monitored repository. Duplicate paths (including root/work aliases) are rejected. A moved or unavailable folder remains listed and shows an error when opened; restore its path/mount or register its new location. Removal and renaming in the UI are not included yet.

Native registrations are saved in `${XDG_DATA_HOME:-~/.local/share}/workweave/projects.json`; override with `--data-dir` or `WORKWEAVE_DATA_DIR`. Run one server process per data directory. A corrupt registry produces an error without overwriting the file; restore it from a backup or move it aside to start a fresh library.

This is a personal local service without authentication. Native startup and Docker publishing default to loopback. HTTP requests validate Host/Origin and do not enable cross-origin access. Do not expose it as a public server.

---

## ⚙️ Configuration

| Option | CLI Flag | Environment Variable | Default | Description |
|---|---|---|---|---|
| Target Path | `--target`, `-t` | `WORKWEAVE_TARGET` | None for server; `.` for exports | Optional startup registration; repo root or `work/` dir |
| Port | `--port`, `-p` | `WORKWEAVE_PORT` | `8088` | HTTP port |
| Host | `--host` | `WORKWEAVE_HOST` | `127.0.0.1` | Native host interface (container listens on `0.0.0.0`) |
| Title | `--title` | `WORKWEAVE_TITLE` | `None` (auto-detected) | Custom dashboard title |
| Registry directory | `--data-dir` | `WORKWEAVE_DATA_DIR` | XDG data directory / `workweave` | Persistent project registry |
| Allowed parent | `--projects-root` | `WORKWEAVE_PROJECTS_ROOT` | Unrestricted natively; `/projects` in Docker | Restrict registered paths to a parent folder |
| Build Export | `--build`, `-o` | — | `None` | Export static HTML and exit |
| JSON Export | `--json` | — | `false` | Dump state JSON to stdout |

### Project API

`POST /api/projects` accepts `{"path":"/absolute/project","name":"Optional title"}` as JSON, with `X-WorkWeave-Request: 1`. It returns `201` with `{"project":{"id":"…","name":"…","path":"…/work"}}`. `GET /api/projects` returns `{"projects":[…]}`. IDs are stable across restarts. Names are limited to 120 characters; request bodies to 16 KiB.

`GET /api/folders` returns `path`, `parent` (null at the boundary), `start`, `directories` (name/path pairs), `truncated`, `selectable`, and `reason`. It is read-only and uses the same Host/Origin checks as the project API. Files and symlinks outside the configured root are omitted. Missing folders return `404`; unreadable folders return `403`; paths outside the root return `400`.

Errors use `{"error":{"code":"…","message":"…"}}`: invalid input `400`, duplicate or unavailable project `409`, unknown ID `404`, wrong origin/header `403`, wrong content type `415`, oversized body `413`, storage failures `500`. Legacy state endpoints require a project ID when zero or multiple projects are registered. An explicit startup `--target` is retained for migration; existing registrations are reused, and their saved names are preserved.

---

## 📁 Expected Directory Structure

WorkWeave parses the standard agent workflow structure:

```text
my-project/
└── work/
    ├── INDEX.md                     # High-level list of work items & statuses
    ├── work-001-setup/
    │   ├── README.md                # Item goal & background
    │   ├── tasks.md                 # Markdown task checklist (- [x] 1.1 ...)
    │   ├── decisions.md             # Architecture decisions log
    │   ├── coordination.md          # Active agent coordination & handoffs
    │   └── tasks/
    │       └── task-1.1.md          # Task contracts with scope & acceptance
    └── work-002-feature/
        ...
```

---

## 🧪 Testing

Run test suite:

```bash
python3 -m unittest discover tests
```

---

## 📄 License

MIT License.
