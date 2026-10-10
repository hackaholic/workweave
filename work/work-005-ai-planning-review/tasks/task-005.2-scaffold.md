# Task 005.2 — Replace misleading scaffold behavior

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005

## Objective
Make scaffold preparation idempotent, non-destructive and honest about its role.

## Context and scope
Read [parent architecture and lifecycle](../README.md) and [decisions](../decisions.md).
- Preserve original request and existing notes/contracts; create only missing skeleton files unless a reviewed replacement is explicitly requested.
- Remove hardcoded agent ownership and automatic In Progress promotion; show Prepare structure separately from Plan with AI.
- Repeated clicks/retries must not overwrite changes, create duplicate contracts or lose multiline user text.
- Out of scope: unrelated refactoring, new storage backend, automatic implementation, or shared-skill modifications.

## Dependencies and files
- Depends on: 005.1
- Inspect/edit: scaffold_draft_work, creation/scaffold endpoints, dashboard action labels and fixture tests.

## Test cases

| ID | Trigger | Expected outcome | Status |
| --- | --- | --- | --- |
| SC-01 | Prepare/repeat a draft containing multiline notes | Original text and edits retained; no fabricated owner/status | Pass — see notes.md |
| SC-02 | Prepare a reviewed or active work item | No reset/overwrite of plan, approval or execution state | Pass — see notes.md |
| SC-03 | Write failure during preparation | Recoverable error and preserved existing data | Pass — see notes.md |

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

Implementation verified by lifecycle, preparation and HTTP integration tests; final browser/recovery checks tracked in 005.5.
