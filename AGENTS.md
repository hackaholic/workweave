# WorkWeave project guidance

Shared coding skills are mapped in [SKILLS.md](SKILLS.md). Read that mapping and load only the skill relevant to the current task.

WorkWeave is a local Python application that reads Markdown workflow folders. Its main modules are `workweave/parser.py` (data parsing), `workweave/dashboard.py` (HTML and JavaScript), `workweave/server.py` (HTTP endpoints), and `workweave/cli.py` (configuration and exports).

Keep changes appropriate for a personal, single-user local tool. Preserve the standard-library runtime unless a requested feature justifies a dependency. Comments, editing, and database storage are not implemented merely because they have been discussed.

Run relevant checks for behavior changes; the existing suite is `python3 -m unittest discover tests -v`. HTTP tests bind a local loopback port. For UI changes, also verify the affected browser behavior when available.

For work managed by `workflow.json`, use the lifecycle API: inspect the current plan and version, submit planning results, wait for explicit user review, and claim/start only the approved revision. Do not manufacture approval, edit lifecycle metadata directly, or treat preparation as AI work. If scope changes, request changes and submit a new revision. External editor changes cannot be prevented by the app; plan-bearing Markdown changes invalidate approval. Historical work without lifecycle metadata remains readable; explicit enrollment is required for implementation through the app.

New lifecycle code lives in `schemas/`, `repositories/`, `services/`, `controllers/`, and `views/`, with review assets in `templates/` and `static/`. Keep additions modular; broader extraction of the older dashboard/server is tracked in Work004.
