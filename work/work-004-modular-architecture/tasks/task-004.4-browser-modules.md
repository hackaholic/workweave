# Task 004.4 — Extract browser modules and event handling

**Owner:** Unassigned
**Role:** Frontend engineer
**Status:** Pending
**Work item:** Work 004

## Objective
Move JavaScript out of Python/HTML into focused modules for API access, state, rendering, dialogs, folder browsing and workflow actions.

## Context and contract
Read [architecture and compatibility rules](../README.md) and [decisions](../decisions.md). Existing functionality is the migration baseline; do not add unrelated features.

## Scope
- Use ordered classic deferred scripts and one intentional namespace so live and file:// export modes share code; avoid globals for individual actions and remove inline event handlers.
- Bind events via listeners/delegation and stable data attributes; render untrusted labels/comments safely and centralize API errors/project identity.
- Preserve folder abort/generation handling, filters/KPI selection, comments, title/toggle/new task actions, work creation/scaffolding and dialogs; export mode must not bind network write actions.
- Out of scope: changes excluded by the parent work item.

## Dependencies and relevant files
- Depends on: 004.2; coordinate final classes with 004.3.
- Inspect/edit: static/js/core/, projects/, dashboard/, projects-page.js, dashboard-page.js; template data hooks and view JSON bootstrap.

## Test cases (defined before implementation)

| ID | Category | Trigger | Expected outcome | Status |
| --- | --- | --- | --- | --- |
| JS-01 | happy | Exercise existing project/workflow UI flows | Same user-visible results with correct selected project/work IDs | Not run |
| JS-02 | failure | Failed request, rapid folder navigation and modal close during fetch | No stale selection/double submission; useful recovery and focus behavior | Not run |
| JS-03 | security | Hostile labels/comments/filenames and same-origin writes | No script execution; required API headers preserved | Not run |
| JS-04 | regression | Open standalone HTML via file:// | Filters and contract dialogs work; mutations disabled and no API fetch attempts | Not run |

Verification: Browser interaction matrix and console inspection; meaningful pure-JS/state tests if a suitable local runner is available, without making Node a runtime dependency.

## Security validation
Replace inline JavaScript string interpolation with data bindings. Use textContent/DOM helpers for untrusted data; preserve API checks and race protections.

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
