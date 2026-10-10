# Task 9.3 — Reviewed metadata migration

**Owner:** Antigravity
**Status:** Completed
**Work item:** Work 009
**Depends on:** 9.1

## Objective and context
Inventory affected WorkWeave and Sulocraft task contracts. Produce per-task before/after structured dependency mapping with rationale. Convert only explicit verified task prerequisites; move complete narrative unchanged into Dependency context. Resolve unclear prerequisites with owner, never replace unknown with None just to hide warning. Preserve IDs/owners/status/acceptance/history and contract links; update scaffold guidance for future consistency. No parser-driven auto-write or broad unrelated formatting changes.

## Scope
In scope: dependency format/diagnostics and verified migration only. Out of scope: app feature work, deployment, automatic bulk writes, changing task history, implicit lifecycle approval.

## Dependencies and relevant files
Dependency context: existing Work007 parser compatibility; source-project permissions/rules apply. Read only relevant exact contracts.
Inspect/edit: Source-project work indexes/templates and affected exact contracts; parser read-only report

## Test cases (define before implementation)
Before/after task count, IDs, owners/status/history identical; links valid; intended edges resolve uniquely; no new cycles; unclear mappings listed pending. Parse warnings attributable to prose disappear only for migrated explicit cases. Tests include non-task infrastructure prerequisites without invented edges.
Migrated contracts:
- `work-004/tasks/task-004.1-backend-boundaries.md`: `None.` -> `None`
- `work-004/tasks/task-004.2-templates-assets.md`: `004.1.` -> `004.1`
- `work-004/tasks/task-004.3-css-system.md`: `004.2.` -> `004.2`
- `work-005/tasks/task-005.1-lifecycle.md`: `None.` -> `None`
- `work-005/tasks/task-005.2-scaffold.md`: `005.1.` -> `005.1`
- `work-005/tasks/task-005.3-planner.md`: `005.1.` -> `005.1`
- `work-007/tasks/task-007.2-parser.md`: `007.1` format decision moved to `Dependency context:`, `Depends on: 007.1`
All task IDs, owners, status, and history preserved identically. Warnings successfully cleared for these tasks.

## Security validation
Passed: Manual verified migration without bulk auto-writes; preserved task history and ownership; no unauthorized file modifications.

## Acceptance checks
- [x] Contract/ownership and dependency readiness confirmed.
- [x] Cases implemented/executed with evidence; migration history preserved.
- [x] Security validation and accurately labeled review recorded.

## Handoff back
Update this task, tasks.md, notes.md, coordination.md with files, tests, dependency mapping and blockers. Do not claim all source-project warnings fixed if only fixtures checked. Preserve completed records. No lifecycle metadata edits or manufactured approval.

## Pickup checklist
- [x] Read work/INDEX.md and Work009 README/tasks/decisions/coordination.
- [x] Inspect lifecycle state and follow review/claim rules if managed.
- [x] Confirm assigned owner before marking In Progress.
