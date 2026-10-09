# Work 005 — AI planning and review before implementation

## Objective
Turn a simple user draft into a reviewed, actionable plan without pretending template generation is AI work, inventing an agent assignment, or starting implementation prematurely.

## Status
Completed — Codex implemented and verified 005.1–005.5. See notes.md for test, browser and Docker evidence.

## Required lifecycle
Draft → Planning → Ready for review → Ready to implement → In progress → Completed.

- Creation preserves the original user request as a separate, immutable revision alongside the evolving plan.
- Planning begins only when a real planner accepts the work. The planner inspects relevant project context and returns scope, assumptions/questions, architecture where needed, dependencies, subtasks and acceptance checks.
- Template preparation may create missing structure but never counts as AI planning, review, assignment or implementation.
- The user reviews the proposed plan and explicitly approves its current revision or requests changes. Unresolved required questions prevent approval. Changed scope, task objectives or acceptance checks invalidate prior approval; execution notes and progress updates do not.
- Approval makes work ready; a separate claim/start action records the actual executor and begins implementation. Unapproved work and tasks cannot start through supported API/UI paths.
- Failed/cancelled planning preserves the draft and last good plan, exposes retry, and never silently promotes the lifecycle. Request changes returns to Draft with feedback preserved, awaiting a fresh planner pickup.

## Architecture and persistence
Use explicit workflow transition services in the existing local modular monolith, a file-backed lifecycle record and immutable request/plan revisions. Reuse Markdown work folders and task contracts; no database or autonomous background worker is required.

Final storage decision: `workflow.json` contains the preserved request, immutable plan revisions, revision-specific progress, approval, run/executor identity and audit history in one atomic snapshot. The review page renders human-readable views. Existing Markdown remains unchanged context/history, not a second synchronized authority. See [lifecycle contract](lifecycle-contract.md).

Keep the planning phase distinct from the existing Completed/In Progress/Pending/Blocked execution status, with a documented mapping for legacy consumers. Do not let the old parser silently collapse review states into Pending. Use atomic updates, conflict detection and recovery for related file updates; never partially approve a plan.

## AI execution boundary
A template generator is not a planner. Provide a planner adapter contract and an explicit externally assisted handoff mode. In handoff mode the UI exports a pickup prompt/context manifest; a real agent returns a plan that the app validates and records. Label this mode clearly: it does not invoke AI itself.

A one-click AI planning option may only appear enabled after a concrete supported provider/agent runner is configured and tested. Provider choice, credentials, execution location and permitted context must be resolved before implementing invocation; inspect available integration first rather than assuming a Codex/chat API exists. Never silently substitute generic templates. Do not execute AI-produced commands, arbitrary callback URLs or raw filesystem paths. Send only the selected project's authorized context and never log credentials.

## Enforcement boundary
The local application must enforce revision-aware approval in its transition and mutation endpoints, not just hide buttons. Shared agent instructions must check the same approval record before implementation. The application cannot technically stop an external editor or agent that bypasses its API and directly edits repository files; document this limit and detect stale/mismatched approval at the next read/start.

## Compatibility and scope
Preserve Work 001–003 features and historical records. Handle legacy drafts, template-scaffolded In Progress items and genuinely active/completed work conservatively; never invent approvals or silently reset ongoing work. Inspection, comments and planning feedback stay available while implementation is gated. Define each existing mutation endpoint's permitted phases explicitly.

Coordinate with Work 004 modular architecture: use the module layout actually present when picked up. Work 004 is not a hard prerequisite; do not perform a second broad refactor here. Update project-local guidance only; shared skill changes remain a separate approval-controlled task.

## Done when
No scaffold action falsely reports AI work or assigns Antigravity; requests and plan revisions are retained; a real planning return is distinguishable from preparation; users can review/approve/request changes; supported start and implementation-write paths reject missing/stale approval; migration and failure scenarios pass.
