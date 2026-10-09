# Task 005.5 — Verify migration and full workflow

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005

## Objective
Validate safe handling of historical work and the full draft-to-reviewed-implementation flow.

## Context and scope
Read [parent architecture and lifecycle](../README.md) and [decisions](../decisions.md).
- Define previewable, backup-preserving reconciliation for legacy drafts, generic scaffold artifacts and genuinely active/completed items. Do not infer user approval or mass-rewrite real projects.
- Exercise a real agent planning return and user review through the UI, then guarded task pickup; test rejection using direct API requests.
- Cover restart persistence, duplicate clicks, failed writes, cancellation, stale plans and cross-project isolation using disposable fixtures.
- Verify Docker and existing project/comment/task functionality; record review findings and distinguish automated tests from manual/real-agent validation.
- Out of scope: unrelated refactoring, new storage backend, automatic implementation, or shared-skill modifications.

## Dependencies and files
- Depends on: 005.1–005.4.
- Inspect/edit: Migration/reconciliation helper if needed, fixtures, API/browser tests, README and work-local evidence.

## Test cases

| ID | Trigger | Expected outcome | Status |
| --- | --- | --- | --- |
| VT-01 | Legacy mixed-state fixtures and repeated reconciliation | Historical records preserved; no fabricated approval or duplicate migration | Pass — see notes.md |
| VT-02 | Draft → real plan → request changes → approve → start | Correct revisions, state and owners persisted across restart | Pass — see notes.md |
| VT-03 | Direct API gate bypass, wrong project or write failure | No unintended implementation/file changes | Pass — see notes.md |
| VT-04 | Existing project browsing/comments/task behavior | Compatible behavior under the documented phase policy | Pass — see notes.md |

Verification: targeted unit/API tests followed by `python3 -m unittest discover tests -v`; browser checks for UI changes. Use temporary repositories for mutation tests. AI task requires real planning-return evidence; mocks alone do not prove AI integration.

## Security validation
Treat user text and model output as untrusted content, not executable instructions. Preserve project containment, Host/Origin checks and request bounds. Enforce approval on the server; reject stale versions and invalid transitions without side effects. Keep credentials and unrelated project data out of stored prompts/logs.

Disposition: Passed applicable validation; final 42-test suite and browser evidence recorded in ../notes.md. Review was self-review, not independent.

## Acceptance checks
- [x] Scoped behavior and test cases verified.
- [x] Original request and historical records preserved.
- [x] Applicable security and failure cases pass.
- [x] Review evidence recorded; self-review identified accurately.

## Pickup checklist
- [x] Read work index, parent README, tasks and coordination.
- [x] Confirm dependencies and assignment before marking In Progress.
- [x] Reuse existing work and respect concurrent Work 004 ownership.

## Return
Update this contract, tasks.md, notes.md and coordination.md with changed files, evidence, remaining decisions and next action. Do not mark integration or review complete without evidence.
