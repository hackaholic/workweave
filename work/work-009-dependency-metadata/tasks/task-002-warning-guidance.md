# Task 9.2 — Actionable diagnostics

**Owner:** Antigravity
**Status:** Completed
**Work item:** Work 009
**Depends on:** 9.1

## Objective and context
Make dependency-format warning explain why no edges were created and show how to separate IDs from prose. Keep dependency inference strict; do not automatically scrape IDs from narrative. Keep existing unknown-reference and cycle diagnostics distinct. Escape document content in UI and avoid unrelated dashboard redesign.

## Scope
In scope: dependency format/diagnostics and verified migration only. Out of scope: app feature work, deployment, automatic bulk writes, changing task history, implicit lifecycle approval.

## Dependencies and relevant files
Dependency context: existing Work007 parser compatibility; source-project permissions/rules apply. Read only relevant exact contracts.
Inspect/edit: workweave/workflow_format.py; parser.py; dashboard/views; tests

## Test cases (define before implementation)
Regression: valid IDs/links produce edges, prose produces actionable warning without inferred edges, malformed/unknown/ambiguous/cyclic refs retain diagnostics. UI displays guidance escaped; malicious Markdown/HTML cannot execute. Existing compatibility suite passes.
Concrete test: `test_dependency_actionable_warnings` in `tests/test_workflow_format.py`. Verified with `python3 -m unittest discover tests -v`.

## Security validation
Passed: Display values escaped via escapeHtml in `workweave/static/workflow-metadata.js`. Warnings are rendered safely as escaped HTML text. Strict dependency regex prevents arbitrary script injection or unexpected dependency graphs.

## Acceptance checks
- [x] Contract/ownership and dependency readiness confirmed.
- [x] Cases implemented/executed with evidence; migration history preserved.
- [x] Security validation and accurately labeled review recorded.

## Handoff back
Update this task, tasks.md, notes.md, coordination.md with files, tests, dependency mapping and blockers. Do not claim all source-project warnings fixed if only fixtures checked. Preserve completed records. No lifecycle metadata edits or manufactured approval.

## Pickup checklist
- [x] Read work/INDEX.md and Work009 README/tasks/decisions/coordination.
- [x] Inspect lifecycle state and follow review/claim rules if managed.
- [x] Confirm assigned owner before marking In Progress.
