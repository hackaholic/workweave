# Task 004.5 — Verify compatibility and distribution

**Owner:** Unassigned
**Role:** Test / review
**Status:** Pending
**Work item:** Work 004

## Objective
Verify the modular application end-to-end, including installed resources, standalone exports and Docker, then update project documentation and complete the work item.

## Context and contract
Read [architecture and compatibility rules](../README.md) and [decisions](../decisions.md). Existing functionality is the migration baseline; do not add unrelated features.

## Scope
- Run the full suite and compare the captured baseline; verify all current mutation flows using temporary repositories and preserve existing user data.
- Build wheel and sdist, install the wheel in an isolated environment outside the checkout and verify templates/static assets/CLI; rebuild Docker and verify persistence and mount behavior.
- Verify live and offline browser flows, responsive CSS, keyboard dialogs, error states and no external styling dependency; update guidance to the implemented module layout and record review disposition.
- Out of scope: changes excluded by the parent work item.

## Dependencies and relevant files
- Depends on: 004.1–004.4.
- Inspect/edit: tests/, pyproject.toml, Dockerfile if needed, README.md, AGENTS.md and this work package; migrated modules only for verified regression fixes.

## Test cases (defined before implementation)

| ID | Category | Trigger | Expected outcome | Status |
| --- | --- | --- | --- | --- |
| IN-01 | regression | Full suite and recorded Work 001–003 behavior matrix | No unexplained route/state/file-format regression | Not run |
| IN-02 | distribution | Installed wheel from unrelated cwd and Docker startup/restart | Assets render; registrations persist; mounts and health remain correct | Not run |
| IN-03 | regression | Export standalone HTML, stop server and open file locally | Styling/filter/contract inspection work; write actions clearly disabled | Not run |
| IN-04 | security | Repeat escaping, path-boundary, wrong-origin and invalid mutation cases | No disclosure, script execution or unintended writes | Not run |

Verification: python3 -m unittest discover tests -v; git diff --check; package build/install smoke tests; docker-compose config --quiet and docker-compose up -d --build; browser evidence.

## Security validation
Review new static-serving/template boundaries and existing writable workflow boundaries. Record findings, fixes and remaining limitations; label self-review accurately.

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
