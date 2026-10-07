# Work 003 — Interactive KPI Filtering, Comments, and Work/Subtask Scaffolding

## Objective
Make top KPI cards interactive filter toggles (including a dedicated Blocked category), allow adding comments and editing on work and subtask levels, and enable creating new user draft work items and subtasks with on-demand AI scaffolding.

## Architecture
- **Parser & Mutation (`workweave/parser.py`)**:
  - Extend dataclasses (`WorkItem`, `SubTask`, `Comment`) to hold comments, notes, and draft status.
  - Parse `comments.md`, `notes.md`, and draft metadata.
  - Provide safe markdown mutation functions (`add_work_comment`, `update_subtask`, `create_work_item`, `create_subtask`, `scaffold_draft_work`).
- **HTTP Server (`workweave/server.py`)**:
  - Add REST API endpoints:
    - `POST /api/comments`: Add work-level or subtask-level comment.
    - `POST /api/subtasks/toggle`: Toggle or update subtask completion/title.
    - `POST /api/subtasks/new`: Add a new subtask.
    - `POST /api/work/new`: Create a draft work item.
    - `POST /api/work/scaffold`: Formally scaffold a draft work item.
- **Dashboard UI (`workweave/dashboard.py`)**:
  - Interactive clickable KPI cards (`Total`, `Completed`, `In Progress`, `Pending`, `Blocked`).
  - Work-level comments thread with input form.
  - Subtask-level comments view, inline title editing, and checkbox toggling.
  - "+ New Work Item" modal with draft badge.
  - "+ Add Subtask" quick input.
  - "🤖 AI Scaffold Work" trigger button to promote drafts to structured packages.

## Scope
- In scope:
  - Interactive KPI filtering + Blocked pill & count.
  - Comments on work items and subtasks stored in `comments.md`.
  - Subtask editing & checkmark toggling synced to `tasks.md`.
  - New work items created with distinct draft state.
  - AI scaffolding action converting draft into full `work/` folder package.
  - Unit tests in `tests/test_parser.py` and `tests/test_server.py`.
- Out of scope:
  - External database integration (maintain zero dependencies & local markdown source of truth).
  - Deleting monitored projects or external files.

## Status
In Progress.
