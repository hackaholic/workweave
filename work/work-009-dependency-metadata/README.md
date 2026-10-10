# Work 009 — Structured dependency metadata and warning repair

**Owner:** Antigravity (coordination lead)
**Status:** Completed

## Objective
Make task dependency metadata consistently machine-readable so WorkWeave can show prerequisite connections accurately, while preserving human context and completed history.

## Confirmed issue
workflow_format.dependencies() accepts only an entire comma/semicolon-separated list of dotted task IDs or Markdown .md links. enrich() emits “Dependency prose retained; no structured dependency inferred.” when a nonempty Depends on value is prose. Sulocraft examples include “Returned18.2/18.3/18.4; reuse Work017 components.” Such text is preserved but contributes no dependency edges. This is a document-format issue; the parser deliberately avoids guessing prerequisites from prose.

## Scope
Document/schema guidance, better actionable warning UI, explicit metadata migration with review, regression and browser acceptance. Preserve standard-library runtime. Do not silently infer IDs embedded in narrative, suppress real warnings, change task ownership/status/history, or implement an automatic cross-project bulk writer.

## Dependencies and authority
Relevant Work007 compatibility behavior is already implemented. WorkWeave owns format guidance/parser diagnostics; Sulocraft work contracts remain owned in /home/anu/git/crochet. Cross-project migration requires reviewed mapping and applicable project rules. No workflow.json enrollment or approval is implied by this planning-only work; any managed implementation must follow the lifecycle planning/review/claim API before work starts.

## Done when
Canonical metadata guidance and actionable diagnostics exist, a reviewed mapping is applied without data loss, valid edges/unknown references/cycles remain correctly reported, and test/browser evidence confirms the displayed prerequisite relationships.
