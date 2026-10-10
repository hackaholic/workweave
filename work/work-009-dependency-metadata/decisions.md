# Decisions

- Depends on contains only task IDs/contract links or explicit None. Describe infrastructure and implementation prerequisites under Dependency context, not the structured field.
- None means no task edges, not “ignore existing prerequisites”. Unknown remains unresolved and must not be substituted with None just to silence a warning.
- Preserve narrative verbatim during migration; convert references only after validating each intended prerequisite. No guesses from any number in text.
- WorkWeave reads source documents without rewriting them at runtime. Diagnose malformed metadata with a valid example, preserving unknown/ambiguous/cyclic reference warnings.
- Completed records and acceptance history remain intact. Planning-only docs do not confer lifecycle approval.
