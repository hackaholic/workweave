# Lifecycle contract (005.1)

## Authoritative storage
`workflow.json` schema 1 is the sole atomic commit record: original request and its hash, version, phase, append-only plan revisions and their hashes, planner run, approval, executor and audit events. Original text and old plan content are immutable through the service. Human-readable request/plan material is returned by the review/handoff APIs from this record; do not make sidecar Markdown the second authority. Existing README/tasks/notes/contracts are preserved during enrollment.

This deliberately replaces the proposed multi-file commit with one atomic snapshot (`fsync` + replace). A failed save retains the entire previous state; no partly approved plan exists. One application process per workspace; its writes are serialized. Agents use the HTTP protocol rather than editing lifecycle JSON directly. Direct external filesystem editors cannot be technically prevented and are outside this local trust boundary.

## Transitions
- Draft → Planning: real planner `accept_planning`, recording identity and unique run ID.
- Planning → Ready for review: `submit_plan` by the matching planner/run; validate structured output and dependencies.
- Planning → Draft: `cancel_planning` or `fail_planning` for matching run; preserve previous plans.
- Ready for review → Ready to implement: `approve`, only with no unresolved required questions and unchanged reviewed context.
- Ready to implement → In progress: explicit `start`, records executor.
- In progress → Completed: explicit `complete`, requires valid approval and verification evidence.
- Review/ready/active/completed → Draft: `request_changes` with feedback; invalidates approval and waits for a real planner claim. The UI must not pretend a planner is already active.
- Review/ready → Planning: an explicit planner accepts a new revision; old approval is invalidated.

Every transition requires exact `expected_version`; stale/duplicate requests return 409. Plan content is plain data, never executable instructions.

## Context and approval
Approval binds revision/hash and the fingerprint of README, task definitions and task contract files. Checkbox progress, owner/status fields and notes/comments do not invalidate scope approval. Direct changes to objectives, titles, dependencies or acceptance do. Corrupt JSON, changed request/plan hashes and unsafe paths fail closed. External changes require a new planning return/review.

## Execution status mapping
Draft, Planning, Ready for review and Ready to implement map to Pending for existing status consumers. In progress maps to In Progress; Completed maps to Completed. Expose the separate lifecycle phase in API/UI; do not infer approval from old status labels.

## Existing mutations
- Read, browse, comments/feedback: available throughout the lifecycle.
- Create work: always an unapproved Draft, regardless of old `is_draft` input.
- Prepare scaffold: missing structure only; never starts implementation.
- Add/rename task definitions: planning input only before review; after submission use Request changes and submit a new plan.
- Toggle approved-plan tasks: only after explicit executor start and current approval.
- Legacy work: read/comment unchanged; adoption is explicit and non-destructive. Missing approval cannot authorize new implementation writes through the API.
