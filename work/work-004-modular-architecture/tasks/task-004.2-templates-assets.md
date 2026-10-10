# Task 004.2 — Introduce safe templates and packaged resources

**Owner:** Unassigned
**Role:** Engineer
**Status:** Pending
**Work item:** Work 004

## Objective
Replace giant HTML string generation with trusted template files, named partials and explicit view contexts; deliver packaged CSS/JS safely and support standalone export composition.

## Context and contract
Read [architecture and compatibility rules](../README.md) and [decisions](../decisions.md). Existing functionality is the migration baseline; do not add unrelated features.

## Scope
- Use the README rendering contract; start by extracting existing content so application behavior stays runnable while later tasks restructure CSS and JS.
- Serve only explicitly packaged static assets with correct MIME types; reject traversal/unknown files. Never expose project files or permit client-selected template names.
- Preserve generator signatures and load resources with importlib.resources; add package-data declarations and inline the same sources for export mode.
- Out of scope: changes excluded by the parent work item.

## Dependencies and relevant files
- Depends on: 004.1
- Inspect/edit: views/, templates/, static resource manifest/allowlist; controllers/pages.py and http.py; dashboard.py, project_ui.py, pyproject.toml and rendering/export tests.

## Test cases (defined before implementation)

| ID | Category | Trigger | Expected outcome | Status |
| --- | --- | --- | --- | --- |
| TM-01 | happy | Render library/dashboard/error pages from fixtures | Expected data and shared partials; unresolved placeholders fail visibly | Not run |
| TM-02 | security | Titles/comments containing quotes, HTML and closing script tags | Content stays inert text; serialized state round-trips | Not run |
| TM-03 | security | Request encoded traversal, unknown asset and repository-private paths | No filesystem disclosure; defined 404/400 responses | Not run |
| TM-04 | regression | Render and export using installed package from unrelated cwd | Resources resolve; no repository-relative dependency | Not run |

Verification: python3 -m unittest discover tests -v; isolated resource/HTTP/render tests plus export smoke check.

## Security validation
Templates are trusted package resources; text and JSON contexts require distinct escaping. Test TM-02/TM-03. Raw HTML is limited to renderer-created fragments.

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
