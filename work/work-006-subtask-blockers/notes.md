# Verification — 2026-10-10
- Parser now carries task status from section headings and linked blocked contracts; completion overrides stale blocker metadata. Managed plan tasks retain lifecycle authority.
- Blocked count/filter includes affected work once, preserving parent execution status. Added fixed, escaped-status badges to checklist rows.
- Regression test covers section blockers, contract-only blockers, heading reset, completed tasks, unchanged parent status/counts and resolved blockers.
- `python3 -m unittest discover tests -v`: 43 passed. `git diff --check`: passed.
- `docker-compose up -d --build`: succeeded. Browser verified Crochet Blocked (1) -> Showing 1 of 16, Work001 retained In Progress, 1.9.2 rendered with Blocked badge and dependency text.
- Self-review/security: no new writes, dependencies or untrusted HTML interpolation. Crochet files were only read. No independent review claimed.
