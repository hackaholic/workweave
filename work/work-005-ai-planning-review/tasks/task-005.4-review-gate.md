# Task 005.4 — Add review and guarded implementation pickup

**Owner:** Codex
**Status:** Completed
**Work item:** Work 005

## Objective
Let the user review a proposed plan and enforce explicit revision-bound approval before implementation starts.

## Context and scope
Read [parent architecture and lifecycle](../README.md) and [decisions](../decisions.md).
- Show original request beside refined scope/tasks/acceptance and unresolved questions; distinguish approval from task completion.
- Add Approve plan and Request changes with feedback; approval records reviewer/time/revision and yields Ready to implement, not In Progress.
- Require an actual executor claim/start against the approved revision; enforce all phase-dependent mutation rules in the backend, including direct API calls.
- Update project-local pickup guidance to read approval state and document direct-filesystem enforcement limits; do not edit shared skills as part of this task.
- Out of scope: unrelated refactoring, new storage backend, automatic implementation, or shared-skill modifications.

## Dependencies and files
- Depends on: 005.1, 005.2 and 005.3.
- Inspect/edit: Review templates/CSS/JS or current dashboard; transition and mutation endpoints; project-local agent guidance and tests.

## Test cases

| ID | Trigger | Expected outcome | Status |
| --- | --- | --- | --- |
| RV-01 | Approve current complete plan, then explicit executor pickup | Ready to implement followed by In Progress with real owner | Pass — see notes.md |
| RV-02 | Unapproved/stale plan or unresolved required question | Start/mutation denied without side effects | Pass — see notes.md |
| RV-03 | Request changes or concurrent plan edit | Feedback preserved, stale approval rejected, plan returns to review workflow | Pass — see notes.md |
| RV-04 | Keyboard/mobile/loading/error states | Accessible review controls and clear recoverable feedback | Pass — see notes.md |

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
