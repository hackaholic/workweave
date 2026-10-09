# Task 002 — Browse project folders

**Owner:** Codex
**Status:** Completed

## Objective
Browse server-visible folders and select a project from the Add project form.

## Scope
- In scope: directory listing API, modal picker, validation, documentation, tests and local Compose refresh.
- Out of scope: uploads, project deletion, modifying monitored folders, database changes.

## Dependencies and relevant files
Work 001 registry and registration API; projects.py, server.py, project_ui.py, tests and README.md.

## Test cases
| ID | Scenario | Expected result |
| --- | --- | --- |
| FB-01 | Browse default, child, parent and empty folders | Sorted directories only; accurate paths and selectable status |
| FB-02 | Select valid repo or direct work folder | Form fills; Add registers through existing validation |
| FB-03 | Traversal, symlink escape, file/missing/invalid path | No outside listing; structured error; no filesystem mutation |
| FB-04 | Foreign Host/Origin | Rejected with no listing data |
| FB-05 | Unreadable folder and long listing | Recoverable error or bounded result with truncation indicator |
| FB-06 | Browser cancel/Escape, invalid project, rapid navigation, mobile | No stale selection, usable focus and controls |

## Security validation
Read-only directory enumeration shares existing Host/Origin validation. Enforce configured root after resolving symlinks; don't expose file contents. Folder names render via textContent. Add revalidates selection. Negative tests must assert no registry writes.
Disposition: Pass for the local single-user scope. Boundary, malformed path, foreign Host/Origin and no-write checks pass. Folder labels use textContent; selection is revalidated on registration.

## Acceptance checks
- [x] API and negative tests pass.
- [x] Picker selects folders without manual typing and cancellation does not change the form.
- [x] Browser and Docker flow verified.
- [x] Documentation and self-review complete.

## Handoff back
Update work-local evidence and statuses; provide the running app URL.
