# Task 9.1 — Dependency format and templates

**Owner:** Antigravity
**Status:** Completed
**Work item:** Work 009
**Depends on:** None

## Objective and context
Define canonical Depends on examples: None; 18.2, 18.3, 18.4; contained contract links. Put narrative under Dependency context. Clarify infrastructure prerequisites vs task edges, cross-work IDs, unknown prerequisites, and conflict handling. Update WorkWeave task scaffold/template and documented guidance; propose equivalent Sulocraft template update with reviewed source-project change.

## Scope
In scope: dependency format/diagnostics and verified migration only. Out of scope: app feature work, deployment, automatic bulk writes, changing task history, implicit lifecycle approval.

## Dependencies and relevant files
Dependency context: existing Work007 parser compatibility; source-project permissions/rules apply. Read only relevant exact contracts.
Inspect/edit: work/TASK_TEMPLATE.md; workweave/workflow_format.py; scaffold services/templates; compatibility docs/tests

## Test cases (define before implementation)
Canonical task examples parse exactly expected edges; None creates no warning; prose preserved and warned; source task fixtures retain status/owner. Template/scaffold generated through normal path matches guidance.
Add concrete IDs/test files and expected outcomes before implementing. Existing command: python3 -m unittest discover tests -v. Source migrations use read-only parser plus metadata/history/link comparison; backend/UI behavior changes require appropriate tests and local browser check.

## Security validation
Passed: Display values escaped via escapeHtml; template guidance prevents invalid punctuation/prose in Depends on while keeping full narrative under Dependency context. Untrusted Markdown treated strictly without execution.

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
