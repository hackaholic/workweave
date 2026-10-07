# WorkWeave 🧶

**WorkWeave** is a lightweight, zero-dependency multi-agent workflow and task coordination dashboard. It monitors, parses, and visualizes structured project work directories in real time.

---

## ✨ Features

- **Zero Runtime Dependencies:** Pure Python standard library (no pip packages needed to run).
- **Universal Target Resolution:** Point to any repository root with a `work/` folder, or point directly to a `work/` folder.
- **Live Reactive Dashboard:** Modern Tailwind CSS UI with KPI summary, progress bars, search/filter pills, subtask checklist, and interactive contract inspector modals.
- **Dynamic Project Branding:** Automatically infers project titles and adapts seamlessly to any codebase.
- **REST APIs Built-in:**
  - `GET /` — Live HTML Dashboard
  - `GET /api/workflow` / `GET /api/state` — Full JSON workflow state
  - `GET /health` — Health check endpoint
- **Docker-Ready:** Minimal Alpine Linux image with non-root security and healthcheck.

---

## 🚀 Quickstart

### 1. Run Locally (Python)

```bash
# Run against the current project
python -m workweave.cli

# Or point to an arbitrary project or work directory
python -m workweave.cli --target /path/to/project

# Change port and project title
python -m workweave.cli --target /path/to/project --port 8088 --title "My Cool Project"

# Export static HTML snapshot
python -m workweave.cli --target /path/to/project --build ./dashboard.html

# Output JSON to stdout
python -m workweave.cli --target /path/to/project --json
```

### 2. Run with Docker Compose

Set `TARGET_PATH` to the codebase you want to monitor:

```bash
# Start WorkWeave monitoring a project
TARGET_PATH=/home/anu/git/crochet docker compose up -d

# Check health
curl http://localhost:8088/health

# Open in browser
xdg-open http://localhost:8088
```

---

## ⚙️ Configuration

| Option | CLI Flag | Environment Variable | Default | Description |
|---|---|---|---|---|
| Target Path | `--target`, `-t` | `WORKWEAVE_TARGET` | `.` | Path to repo root or `work/` dir |
| Port | `--port`, `-p` | `WORKWEAVE_PORT` | `8088` | HTTP port |
| Host | `--host` | `WORKWEAVE_HOST` | `0.0.0.0` | Host interface |
| Title | `--title` | `WORKWEAVE_TITLE` | `None` (auto-detected) | Custom dashboard title |
| Build Export | `--build`, `-o` | — | `None` | Export static HTML and exit |
| JSON Export | `--json` | — | `false` | Dump state JSON to stdout |

---

## 📁 Expected Directory Structure

WorkWeave parses the standard agent workflow structure:

```text
my-project/
└── work/
    ├── INDEX.md                     # High-level table of work items & statuses
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
