# Task 006.1 — Subtask blockers
**Owner:** Codex
**Status:** Completed

## Scope
Parse task section status with linked contract fallback; count work containing blocked subtasks and show badges. Preserve parent status and completion counts. No changes to monitored projects or lifecycle gates.

## Acceptance and tests
- [x] Blocked section and linked blocked contract are visible; completed tasks are not blockers.
- [x] Parent In Progress remains unchanged; Blocked filter includes it once.
- [x] Full suite and Docker browser verification pass.

## Security
Render status using fixed badges and existing escaped task text. No new write endpoints or dependencies. Self-review required.
