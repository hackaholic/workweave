# Work 007 — Shared workflow and parser compatibility

## Objective
Make WorkWeave reliably understand the maintained ai_skills scaffold while preserving existing Markdown projects and WorkWeave-managed lifecycle records.

## Status
Completed — approved shared patch applied and validated; all five contracts implemented. 49 tests passed, browser verified, and Docker rebuilt. See notes.md.

## Scope and architecture
Use the current work/ tree, filenames and standard-library runtime. Support current bullet and legacy bold coordination fields. Add explicit semantic task IDs without breaking stored comment references or existing mutation IDs. Expose dependencies/blocker details only when reliably expressed; retain original prose otherwise. Establish precedence and surface conflicts. Keep managed JSON lifecycle authority separate from Markdown-only projects.

## Acceptance
Shared template fixtures must parse correctly; legacy fixtures continue working; read-only parse never rewrites monitored repositories; updates preserve unrelated Markdown and comments. No mass migration, database, automatic implementation, renamed folders or weakened approval gates.
