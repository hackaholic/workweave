# Task 005.3 — Integrate real planning and explicit handoffs

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005

## Objective
Receive genuine contextual planning output through a defined agent handoff or configured AI adapter, never a template masquerading as AI.

## Context and scope
Read [parent architecture and lifecycle](../README.md) and [decisions](../decisions.md).
- Inspect supported integrations; document provider/runner, credentials, context permissions and cancellation model before implementing direct invocation. Do not assume a chat automation API.
- Implement an explicit handoff mode with selected-work context manifest and pickup prompt; a validated external return records actual planner identity and plan revision without implying automatic execution.
- Define structured output containing objective, scope/non-goals, assumptions/questions, dependencies, subtasks and acceptance/security checks; validate paths and bound size.
- For a configured direct adapter, require a real end-to-end smoke test; for unavailable configuration, disable direct invocation and clearly offer handoff mode. Failures/retries preserve prior data; reject late or duplicate stale returns.
- Out of scope: unrelated refactoring, new storage backend, automatic implementation, or shared-skill modifications.

## Dependencies and files
- Depends on: 005.1.
- Inspect/edit: Planner service/adapter, pickup/return schema, UI planning controls, configuration documentation and tests.

## Test cases

| ID | Trigger | Expected outcome | Status |
| --- | --- | --- | --- |
| AI-01 | Actual external-agent plan return | Validated contextual plan moves to Ready for review; no implementation starts | Pass — see notes.md |
| AI-02 | Missing configuration, timeout/cancellation or invalid output | Honest recoverable state; no fake success or draft loss | Pass — see notes.md |
| AI-03 | Stale/duplicate result or instructions to run commands/read other projects | Reject unsafe or obsolete output; no arbitrary execution or context leakage | Pass — see notes.md |

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
