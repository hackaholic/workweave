# Task 004.1 — Establish baseline and separate backend responsibilities

**Owner:** Unassigned
**Role:** Backend engineer
**Status:** Pending
**Work item:** Work 004

## Objective
Move data models, pure parsing, filesystem operations and application use cases into their documented layers. Keep server.py as bootstrap/handler composition and route controllers thin.

## Context and contract
Read [architecture and compatibility rules](../README.md) and [decisions](../decisions.md). Existing functionality is the migration baseline; do not add unrelated features.

## Scope
- Capture the actual route/payload/status and public-import baseline before moving code; add missing behavior tests for Work 003 using temporary repositories.
- Move logic incrementally and keep compatibility facades; preserve canonical path checks, registry IDs and Markdown/comment formats.
- Centralize request validation without weakening Host/Origin, size, content-type or project-selection checks; distinguish domain errors from HTTP responses.
- Out of scope: changes excluded by the parent work item.

## Dependencies and relevant files
- Depends on: None.
- Inspect/edit: models.py, errors.py, config.py, controllers/, services/, repositories/, parsing/; existing parser.py, projects.py, server.py, cli.py, __init__.py and tests.

## Test cases (defined before implementation)

| ID | Category | Trigger | Expected outcome | Status |
| --- | --- | --- | --- | --- |
| BE-01 | regression | Parse representative work/checklist/contract/comment fixtures before and after extraction | Equivalent state and public import behavior | Not run |
| BE-02 | happy | Register two projects; exercise comment/task/work mutations on one temporary project | Correct responses and changed files; other project untouched | Not run |
| BE-03 | security | Malformed payload, wrong project, traversal or write failure | Structured failure, no out-of-scope writes or silent data loss | Not run |

Verification: python3 -m unittest discover tests -v; include isolated service/repository and endpoint assertions.

## Security validation
Browser/API payloads and filesystem writes; retain canonical containment, validation and storage failure behavior. Record negative tests BE-03 and any existing unsafe behavior separately.

Disposition: Pending implementation and evidence.

## Acceptance checks
- [ ] Scoped implementation and documented compatibility behavior complete.
- [ ] Test cases pass with evidence recorded in notes.md.
- [ ] Applicable security negatives pass; unresolved findings recorded.
- [ ] Review completed and accurately identified as self-review or independent review.

## Pickup checklist
- [ ] Read work index, parent README/tasks/coordination and this contract.
- [ ] Confirm prerequisites and assignment; mark In Progress before coding.
- [ ] Reuse existing behavior and resources; preserve unrelated working-tree changes.

## Handoff back
Update this contract, tasks.md, notes.md and coordination.md with changed files, verification, blockers and the next dependency-ready task. Mark acceptance only after verification.
