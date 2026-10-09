# Work 005 Notes

## 2026-10-09 — Planning evidence
- Confirmed create_work_item stores user descriptions in README/notes and marks drafts Pending [Draft].
- Confirmed scaffold_draft_work replaces README/tasks/coordination, writes a generic contract, hardcodes Antigravity and promotes the index to In Progress. It has no actual AI invocation or review enforcement.
- Created five pending contracts only. No application edits, external AI calls, shared-skill changes or runtime restart performed.
- Work 004 architecture refactor remains a separate pending package. Preserve existing Work 002 completion edits.

## 005.1 — Lifecycle foundation
- Added schema/validation, atomic repository and transition service modules. Seven targeted tests passed, including competing approvals, stale planner returns, unresolved questions, tampering, scope invalidation and failed atomic replacement.
- Decision: one atomic authoritative record stores original request and plan revisions; sidecar views are not a second transactional store. Single-process workspace ownership is explicit.
- Preserved pre-existing subtask modal and parser/test edits. Continuing with truthful scaffold preparation.

## 005.2–005.4 — Implementation and browser evidence
- Added truthful idempotent preparation, explicit legacy preview/enrollment, structured external-agent pickup/return, revision-aware approval/start/progress/complete policies, and a modular review page. New UI uses separate template/CSS/JavaScript; runtime remains standard-library-only.
- Original requests, plan revisions, feedback and per-revision progress are retained in atomic workflow.json snapshots. Late/duplicate returns and changed work context fail closed. No provider or credentials are assumed.
- Browser smoke on disposable `/tmp/workweave-005-browser` at port 8092: Codex inspected the request and project README, authored a concrete reading-list search plan, raised an unresolved format question, and submitted through the UI. Approval was visibly disabled. A simulated reviewer provided a format decision; Codex submitted revision 2. Simulated review and explicit executor pickup succeeded; dependency-order progress and completion persisted after server restart. No reading-list implementation was performed. Screenshot: `/tmp/work005-review-proof.png`.
- Browser verification caught and fixed an extra parenthesis in dashboard action gating. The reviewed tasks then rendered and progress updates succeeded.
- Self-review (not independent): inspected service/transport/view boundaries, JSON validation, bounded requests/history, filesystem containment, stale revision/run handling, atomic-save failure, HTML text rendering, and retained legacy files. Broader old dashboard/parser/server extraction remains Work004.
- Latest full suite: 40 passed, one failed (41 total). Failure is the legacy completion negative test after a concurrent server.py edit restored unreviewed legacy mutations. This is an unresolved policy/code conflict, not recorded as a passing gate. Earlier suite passed all 38 tests before the additional API/dependency cases and concurrent change.

## 005.5 — Final integration after Gemini finished
- Resumed on user instruction. Preserved Gemini's legacy create/rename behavior and closed a combined title/completion request bypass. Original completion denial test now passes.
- `python3 -m unittest discover tests -v`: **42 tests passed**, including legacy combined-update denial, full HTTP lifecycle, revision conflicts, changed planning context, project isolation, dependency order, malformed metadata and failed atomic replacement.
- `git diff --check`: passed. `docker-compose up -d --build`: passed; container reports healthy on loopback port 8088.
- Final browser inspection of the rebuilt Docker service confirmed the dashboard renders, legacy task completion is disabled while definition editing remains available, and Plan & review loads packaged CSS/JS/template with a non-destructive legacy preview and truthful handoff notice. No real project was enrolled or approved during verification. Earlier disposable browser test covers the full real-agent-return/review/start flow.
- Self-review complete (not independent). No unresolved blocking findings. All five subtasks complete. Work004 remains separate. Direct provider invocation is intentionally unavailable; a real external agent must return the plan. Identities are local declarations, not authenticated accounts; the API cannot prevent direct filesystem edits.
