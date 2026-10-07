# Task 001 — Multiple projects

**Owner:** Codex
**Status:** Completed

## Objective
Deliver persistent UI-driven registration and navigation for multiple local projects.

## Scope
- In scope: registry, HTTP endpoints, library UI, dashboard navigation, CLI/Docker setup and verification.
- Out of scope: comments, task editing, database, remote user accounts, deletion.

## Dependencies and relevant files
Existing parser and generated dashboard; change server.py, cli.py, dashboard.py, Dockerfile, docker-compose.yml and README.md; add projects.py, project_ui.py and tests.

## Test cases
| ID | Scenario | Expected outcome |
| --- | --- | --- |
| TC-01 | Fresh registry and home | No projects; visible add form |
| TC-02 | Add two projects and restart registry | Both retained with stable IDs and isolated workflow data |
| TC-03 | Root/work aliases, blank, missing/file paths, wrong types | Duplicate or validation error; no registry mutation |
| TC-04 | Missing project after registration; corrupt registry | Actionable error; no overwrite or crash of unrelated projects |
| TC-05 | Cross-origin, foreign Host, wrong content type, oversize body | Rejected; no registration |
| TC-06 | Traversal/symlink outside configured root; hostile title | Path rejected; title rendered as text |
| TC-07 | CLI exports and legacy aliases | Exports preserved; ambiguous API selection rejected |
| TC-08 | Browser add, switch, reload, mobile | Correct selected project and usable controls |

## Security validation
Trust boundaries: browser to local API, user paths to filesystem, Markdown to generated HTML. Validate paths/types/size/Host/Origin; atomic registry writes; no writes to monitored repositories. Test denial without side effects. No authentication: loopback defaults and trusted local use only.
Disposition: Pass for this local single-user scope. Negative tests cover invalid inputs, duplicates, path escapes, corrupt/failed storage, foreign Host/Origin, missing write header, wrong content type, oversized bodies and hostile titles. Diff self-review completed; no independent peer review claimed.

## Acceptance checks
- [x] Persistent multi-project API and error cases pass.
- [x] UI onboarding and navigation verified in browser.
- [x] CLI exports and existing parser/server behavior covered.
- [x] Docker setup and usage documented and validated where available.
- [x] Security negatives pass and self-review completed.

## Handoff back
Update tasks.md, notes.md, coordination.md and INDEX.md with results and any limitations.
