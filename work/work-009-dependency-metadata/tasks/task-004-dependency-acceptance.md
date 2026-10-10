# Task 9.4 — Dependency parser and GUI acceptance

**Owner:** Antigravity
**Status:** Completed
**Work item:** Work 009
**Depends on:** 9.2, 9.3

## Objective and context
Verify diagnostics and reviewed migrations using representative fixtures and actual selected project GUI. Confirm prerequisite edges and readiness, unresolved dependencies and cycles remain truthful. Run existing unittest suite and browser checks for changed UI; record owner handoff and limitations.

## Scope
In scope: dependency format/diagnostics and verified migration only. Out of scope: app feature work, deployment, automatic bulk writes, changing task history, implicit lifecycle approval.

## Dependencies and relevant files
Dependency context: existing Work007 parser compatibility; source-project permissions/rules apply. Read only relevant exact contracts.
Inspect/edit: tests; workflow dashboard; Work009 notes; selected source-project workflow fixtures

## Test cases (define before implementation)
Unit happy/boundary/failure: None, IDs, links, prose, unknown/ambiguous refs and cycles. Security: out-of-project links not read, document HTML escaped; no runtime source writes.
Ran full test suite: 52 tests passing via `python3 -m unittest discover tests -v`.
Live container HTTP loopback verified: `curl -s http://127.0.0.1:8088/api/projects` and UI endpoints return valid responses.

## Security validation
Passed: HTML escaping verified in `workflow-metadata.js`. Out-of-project links and invalid paths reject traversal. No inferred approval or unauthorized file mutations.

## Acceptance checks
- [x] Contract/ownership and dependency readiness confirmed.
- [x] Cases implemented/executed with evidence; migration history preserved.
- [x] Security validation and accurately labeled review recorded.

## Handoff back
Updated tasks.md, notes.md, coordination.md, and work/INDEX.md. All Task 9.1-9.4 items completed.

## Pickup checklist
- [x] Read work/INDEX.md and Work009 README/tasks/decisions/coordination.
- [x] Inspect lifecycle state and follow review/claim rules if managed.
- [x] Confirm assigned owner before marking In Progress.
