# Task 007.4 — Display reliable owner, blocker and handoff information

**Owner:** Codex
**Status:** Completed
**Work item:** Work 007

## Objective and scope
Render parsed blocker reason, dependency links, owner and next action with escaped content. Expose missing/conflicting metadata. Do not auto-start work or alter managed lifecycle authority.

## Dependencies and relevant files
- Depends on: 007.2, 007.3
- Inspect/edit: relevant shared proposal/templates for 007.1; parser/schema/services, dashboard/views, tests and compatibility documentation for later tasks. Shared changes need exact proposal approval; no unrelated skills.

## Test cases
- Current scaffold and legacy equivalent: expected fields retained, original bytes unchanged by reads.
- Missing, conflicting or malformed fields: visible unknown/warning; no fabricated owner/dependency/approval.
- Rename/status update: stable semantic identity and existing comments/links retained; unrelated data preserved.
- Managed workflow: unapproved/stale implementation mutations remain rejected.

## Security validation
Treat Markdown and model text as untrusted. Escape display values, contain links/paths, never execute content or read unrelated projects. No new writes outside the selected project. Record applicable negative-test evidence.

## Acceptance checks
- [x] Scoped behavior and compatibility cases verified.
- [x] Relevant checks pass; limitations recorded in notes.md.
- [x] Security and self-review evidence recorded.

## Handoff
Update this contract, tasks.md, notes.md and coordination.md. Do not mark pending validation as passed.

Verified: approved shared patch validation, 49 passing tests, disposable browser and Docker checks. See ../notes.md for evidence and limits.
