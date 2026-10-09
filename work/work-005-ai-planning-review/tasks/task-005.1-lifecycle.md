# Task 005.1 — Define lifecycle and revision contract

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005

## Objective
Specify and implement authoritative phase/revision metadata and allowed transitions, separate from legacy execution status.

## Context and scope
Read [parent architecture and lifecycle](../README.md) and [decisions](../decisions.md).
- Freeze metadata schema, transition table, status mapping and which existing mutations count as planning, feedback or execution.
- Preserve original requests and immutable plan snapshots; use optimistic version checks and atomic/recoverable writes.
- Distinguish planner acceptance, review submission, approval and executor pickup; define request-changes/cancel/failure behavior.
- Out of scope: unrelated refactoring, new storage backend, automatic implementation, or shared-skill modifications.

## Dependencies and files
- Depends on: None.
- Inspect/edit: Current models/parser, workflow services/repositories if Work 004 exists, tests and schema documentation.

## Test cases

| ID | Trigger | Expected outcome | Status |
| --- | --- | --- | --- |
| LC-01 | Valid transition sequence | Draft progresses only through permitted explicit actions | Pass |
| LC-02 | Skip review, stale revision, concurrent approval/edit | Reject conflict without partial writes | Pass |
| LC-03 | Change acceptance/scope versus append execution note | Only meaningful plan changes invalidate approval | Pass |

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

Evidence: seven targeted lifecycle tests passed. Self-review completed. See ../lifecycle-contract.md for schema, transition and mutation policy. Full regression suite runs at the integration boundary.
