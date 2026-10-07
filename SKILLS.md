# Shared coding skills

Skills root: `/home/anu/git/ai_skills`

Resolve the entry points below relative to this root. Change only the root if the shared repository moves. These are references to the shared source, not copied skill instructions.

| When needed | Skill entry point |
| --- | --- |
| Create or migrate a structured `work/` backlog | `workflow-scaffold/SKILL.md` |
| Task pickup, status tracking, and handoffs | `workflow-coordinator/SKILL.md` |
| Feature design and dependencies | `architect/SKILL.md` |
| Dashboard layout, interaction, and accessibility | `ui-designer/SKILL.md` |
| HTTP API and persistence design | `backend-expert/SKILL.md` |
| Implementation | `engineer/SKILL.md` |
| Acceptance and regression test cases | `testcase-skill/SKILL.md` |
| Security checks | `security-validation/SKILL.md` |
| Code review | `peer/SKILL.md` |
| Evidence-based shared skill improvements | `skill-feedback/SKILL.md` |

## Use in WorkWeave

Load only the guidance needed for the current task, rather than the entire suite. For example, a dashboard layout change may need `ui-designer` and `engineer`; a new write endpoint may need `backend-expert`, `engineer`, and relevant test/security guidance. A backend skill does not by itself justify adding a database or framework.

Use the workflow skills when creating or maintaining WorkWeave's own work records. Distinguish those records from another project's `work/` directory that WorkWeave monitors; inspecting the dashboard does not authorize editing that monitored project.

If work records exist, keep acceptance results, decisions, and handoffs with the relevant task. Keep small tasks proportionate, and distinguish self-review from independent review.

If a mapped skill is unavailable, report the missing path rather than inventing its instructions. Shared skill edits require explicit user approval through `skill-feedback`; mapping the skills here does not authorize changing them.

This file provides agent guidance. It does not install skills globally or start a background workflow.
