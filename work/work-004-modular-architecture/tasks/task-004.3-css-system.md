# Task 004.3 — Centralize CSS tokens and UI components

**Owner:** Unassigned
**Role:** UI designer / engineer
**Status:** Pending
**Work item:** Work 004

## Objective
Create an ordered, packaged CSS system shared by the library, dashboard and dialogs, removing runtime Tailwind and inline static styles without changing the product design.

## Context and contract
Read [architecture and compatibility rules](../README.md) and [decisions](../decisions.md). Existing functionality is the migration baseline; do not add unrelated features.

## Scope
- Define semantic color, typography, spacing, border/radius, focus and layer tokens; scope page-specific layouts and reuse component/state classes.
- Cover hover, focus-visible, active, disabled, loading, empty and error states for fields/buttons/cards/dialogs, plus responsive desktop/mobile layouts.
- Remove the external Tailwind runtime only after all rendered and dynamically generated classes have local equivalents; document any validated dynamic-value style helper.
- Out of scope: changes excluded by the parent work item.

## Dependencies and relevant files
- Depends on: 004.2.
- Inspect/edit: static/css/{tokens,base,components,projects,dashboard}.css; templates/ and relevant renderer/JS class names.

## Test cases (defined before implementation)

| ID | Category | Trigger | Expected outcome | Status |
| --- | --- | --- | --- | --- |
| CS-01 | regression | Compare library/dashboard/dialog states at desktop and 390px widths | Recognizable layout, readable content, no unintended horizontal overflow | Not run |
| CS-02 | accessibility | Keyboard navigate and inspect selected/disabled/error states | Visible focus and discernible states with adequate contrast | Not run |
| CS-03 | failure | Open application/export without CDN access | All styles present with packaged assets; no remote styling dependency | Not run |

Verification: Browser state matrix with saved screenshots; existing unittest suite; confirm no runtime CDN style request in migrated pages.

## Security validation
No user-controlled CSS text, arbitrary style URLs or CSS class construction from untrusted strings. Dynamic progress must be validated numeric data.

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
