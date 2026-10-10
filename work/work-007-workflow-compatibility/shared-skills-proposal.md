# Exact shared-skill proposal — approved and applied

Source: `/home/anu/git/ai_skills`. The adjacent patch contains the complete proposed changes to two skill entrypoints, three existing templates and one new format reference. User approved this exact patch; it has now been applied and validated.

Evidence: WorkWeave misses the scaffold's bullet-format handoff fields, does not extract Depends on, restricts checklist owner names, and derives task identity from mutable title text. The existing task template permits prose dependencies, so structured edges must not be invented. The Work005 JSON lifecycle is project-specific and must not become a universal scaffold requirement.

Scope: add optional explicit task IDs, blocker metadata, Blocked checklist section and next-action field; document stable IDs, status ownership, conflict reporting and existing-format compatibility. Preserve folders, filenames, statuses, all acceptance/security gates, and existing records. Missing new fields remain valid. No automatic migration or installed-copy changes: neither workflow skill exists under ~/.codex/skills; WorkWeave references the maintained repository directly.

Expected benefit: consistent new records and an explicit parser compatibility target. Tradeoff: modest additional task metadata and roughly 400–500 words across shared guidance/templates; old prose remains less machine-readable. This does not itself fix WorkWeave parsing.

Validation plan (executed; see notes.md): apply-check the exact patch, run the skill-creator validator where applicable, check relative links, walk through a blocked dependency and an unrelated Markdown-only project, and inspect the diff for preserved tree structure and unchanged gates. Parser regression and round-trip fixtures are tracked separately below. Self-review only; no behavioral agent benchmark claimed.
