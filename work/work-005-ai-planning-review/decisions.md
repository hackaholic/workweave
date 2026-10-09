# Work 005 Decisions

## 2026-10-09 — Preparation, planning, approval and execution are distinct
- Context: The existing scaffold function writes generic templates, assigns Antigravity and marks work In Progress without an AI run or review.
- Decision: Separate idempotent preparation, accepted planning work, reviewed plan approval and explicit execution pickup.
- Consequence: Preparation cannot advance execution status, fabricate an owner or imply AI activity.

## 2026-10-09 — Review is tied to a plan revision
- Context: A checkbox or UI-only gate can be bypassed or remain approved after scope changes.
- Decision: Store request/plan revisions and approval identity; enforce current-revision approval in server-side transition/mutation policies.
- Consequence: Meaningful plan changes require review again. Routine execution updates must not cause approval churn.

## 2026-10-09 — Explicit planning integration, no simulated AI
- Context: WorkWeave currently has no configured AI runtime.
- Decision: Support a clearly named external-agent handoff and validated return protocol; enable direct invocation only with a configured, tested adapter and explicit context boundaries.
- Consequence: Provider selection is a task dependency, not an invented capability. Missing configuration has an honest actionable UI state.

## 2026-10-09 — Preserve legacy planning edits, gate execution
- Gemini's final integration keeps legacy task creation/renaming as planning input. Retain this compatibility without treating it as approval.
- Every completion update, including a combined rename-and-complete request, requires the approved lifecycle execution path. Added a regression test proving rejected combined updates leave tasks unchanged.
