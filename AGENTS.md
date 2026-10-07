# WorkWeave project guidance

Shared coding skills are mapped in [SKILLS.md](SKILLS.md). Read that mapping and load only the skill relevant to the current task.

WorkWeave is a local Python application that reads Markdown workflow folders. Its main modules are `workweave/parser.py` (data parsing), `workweave/dashboard.py` (HTML and JavaScript), `workweave/server.py` (HTTP endpoints), and `workweave/cli.py` (configuration and exports).

Keep changes appropriate for a personal, single-user local tool. Preserve the standard-library runtime unless a requested feature justifies a dependency. Comments, editing, and database storage are not implemented merely because they have been discussed.

Run relevant checks for behavior changes; the existing suite is `python3 -m unittest discover tests -v`. HTTP tests bind a local loopback port. For UI changes, also verify the affected browser behavior when available.
