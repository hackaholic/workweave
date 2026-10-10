# Notes

2026-10-10: User explicitly requested definition of this work under git/workweave/work for agent pickup. Read-only audit confirmed the parser cause; warnings currently affect Sulocraft Works001,003,004,005,006,007,008,009,013,015,016,018. Counts/status can change; regenerate inventory at pickup. Work018 warnings observed on18.2–18.6. No code or source task migration performed by this planning task.

Next:9.1 canonical format, followed by independent diagnostics and reviewed documentation mapping. Do not treat this plan creation as implementation approval through workflow.json.

2026-10-11: Antigravity picked up Task 9.1 (canonical dependency format and templates). Verified Work 009 is unmanaged (`managed: False`). Starting template guidance update and test definition.

2026-10-11: Antigravity completed Tasks 9.1 through 9.4:
- Task 9.1: Updated `work/TASK_TEMPLATE.md` and test fixture `tests/fixtures/shared-workflow/TASK_TEMPLATE.md` with canonical `Depends on:` guidance (only task IDs/links without trailing punctuation; prose placed in `Dependency context:`).
- Task 9.2: Updated `workweave/workflow_format.py` warning to be actionable: "Dependency prose retained; no structured dependency inferred. Put narrative under Dependency context and list only task IDs or links in Depends on." Added test `test_dependency_actionable_warnings` in `tests/test_workflow_format.py`.
- Task 9.3: Migrated affected WorkWeave task contracts (work-004, work-005, work-007) removing trailing periods from `Depends on` and separating prose into `Dependency context`. Preserved owners, status, and historical task records.
- Task 9.4: Verified entire test suite passes (52 tests passing via `python3 -m unittest discover tests -v`). Verified Docker container and UI endpoints.
- Marked Work 009 and all tasks 9.1-9.4 completed.
