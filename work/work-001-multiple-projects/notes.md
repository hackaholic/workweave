# Work 001 Notes

- 2026-10-08: Inspected existing parser, dashboard, CLI, HTTP server, tests and Docker configuration. Existing AGENTS.md and SKILLS.md are untracked user-authorized guidance; preserve them.

## 2026-10-08 — Implementation and verification

- Added `workweave/projects.py` (versioned JSON registry, canonical path validation, atomic writes), `workweave/project_ui.py` (library, form, navigation and error page), project-aware routes in `server.py`, dashboard navigation/escaping, CLI data/root settings, and Docker parent-folder/data-volume configuration. Updated README usage and API contract.
- `python3 -m unittest discover tests -v`: **21 tests passed**. HTTP tests required execution outside the sandbox because sandbox socket creation is denied; no application test failure remained.
- `python3 -m compileall -q workweave tests`: passed. `git diff --check`: passed. No separate linter/type-check configuration exists in this repository.
- `docker-compose config --quiet`: passed. This host uses standalone `docker-compose`; the `docker compose` plugin is unavailable.
- `docker build -t workweave:multi-project-check .`: passed. Disposable container verified health, initially empty library, two UI-equivalent JSON registrations, project-specific state, writes as the image's non-root user, and stable saved IDs after restart. Both project mounts were read-only. Test container and test volume were removed. The first smoke probe raced server startup; bounded readiness polling fixed the test harness and the rerun passed.
- Browser at `http://127.0.0.1:8091`: verified empty onboarding; registration of WorkWeave and a synthetic example; invalid-path feedback; dropdown switching; correct project-specific tasks; saved library after reload. Responsive library checked at 390px; no horizontal overflow. Viewport restored. No browser error logs reported.
- Preview uses `/tmp/workweave-multiproject-preview` for registry data and `/tmp/workweave-preview-example` for the synthetic second project. It does not alter the user's default registry or existing running service. Screenshot: `/tmp/workweave-project-library.png`.

## Acceptance evidence

| Case | Result | Evidence |
| --- | --- | --- |
| TC-01 | Pass | Registry/API empty tests and browser empty state |
| TC-02 | Pass | Registry reload, isolated API states, real container restart |
| TC-03 | Pass | Invalid input and root/work/symlink duplicate tests; no writes on denial |
| TC-04 | Pass | Missing-directory API test, corrupt registry preservation and failed replace preservation |
| TC-05 | Pass | Host/Origin/custom header/content type/size negative API tests |
| TC-06 | Pass | Root traversal/symlink rejection and hostile title escaping tests |
| TC-07 | Pass | CLI exports and legacy single-project/explicit/ambiguous API tests |
| TC-08 | Pass | Browser add, dropdown switch, reload and responsive library checks |

## Self-review and remaining boundaries

- Reviewed changed routes, registry persistence, browser rendering, Docker mounts, CLI compatibility and failure tests using shared peer guidance. Fixed unsafe embedded JSON and inline filename contexts while adding project navigation. No unresolved blocking findings; this is self-review, not independent review.
- Local trusted use only; no remote authentication. One server process per data directory. Project contents remain read-only. Host filesystem visibility is controlled by Docker mounts; projects outside the mounted parent require configuration or a native run.
- Project removal/renaming, comments and task editing remain outside this work package. Existing dashboard styling still uses its external Tailwind script; the new project library uses bundled inline CSS.
