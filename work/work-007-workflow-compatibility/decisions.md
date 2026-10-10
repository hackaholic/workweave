# Decisions

## Preserve compatibility
No directory/filename changes or bulk rewrites. New metadata is additive. Existing Markdown-only projects do not acquire workflow.json. Shared-skill edits and WorkWeave parser implementation are tracked separately.

## Final precedence and identity
Markdown checklist section/checkbox defines task state; contract status is fallback only without a known section. Contract owner is authoritative when present; disagreements are visible. Known labels only are parsed as metadata, avoiding prose-derived false conflicts. Dependency references never fetch arbitrary targets. Managed plans use their lifecycle authority and plan-local dependency IDs.

Semantic task_id is additive; title-based API/comment IDs are preserved. UI rename writes only its selected checklist line with a ww-id marker and retains newline style, owner, number and contract link. No bulk conversion occurs.
