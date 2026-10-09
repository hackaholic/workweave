# Work 002 Evidence

- 2026-10-08: Inspected project registry, API, UI and current Compose setup. Work 001 remains completed; this feature extends its existing registration flow.

## Completed verification — 2026-10-09

- Implemented read-only `ProjectRegistry.browse`, `GET /api/folders`, and the modal folder picker beside the project path input. Updated README with browsing behavior, container scope and endpoint contract.
- `python3 -m unittest discover tests -v`: 27 tests passed during implementation, including six new folder/API tests. Verified sorted directory-only listing, empty valid workflows, native home/root behavior, invalid/file/missing paths, traversal and escaping symlinks, unreadable directories, 1000-entry truncation, special folder names, foreign Host/Origin rejection, and absence of registry writes while browsing.
- `python3 -m compileall -q workweave tests`, `git diff --check`, and `docker-compose config --quiet` passed.
- `docker-compose up -d --build` completed. On resumption, `docker-compose ps` confirmed the service healthy at `127.0.0.1:8088`.
- Browser verified Browse opens `/projects`; invalid project selection and parent navigation above the root are disabled; opening a repository enables selection; selection fills the form; Add project successfully registered WorkWeave and opened its dashboard without typing its path.
- Cancel and Escape left the form unchanged and returned focus to Browse. Up one level returned to `/projects`. The picker was visually checked at a 390px viewport and the viewport was restored.
- Missing-folder UI displays an error and Retry; Starting folder recovers the picker, and a subsequent valid selection fills the form correctly. Saved screenshot: `/tmp/workweave-folder-browser.png`. Test input cleared afterward; existing registered projects preserved.
- Self-review covered read-only enumeration, canonical root checks, safe label rendering and selection state. Superseded requests are aborted and generation-checked; selection is disabled during loading/errors. Race protection was inspected in code, not tested with artificially delayed browser responses. No independent review claimed and no blocking findings remain.

## Remaining boundaries

- Docker can browse only mounted folders under the configured project root; no host-native folder dialog or file upload is used.
- Native browsing starts at the user's home and follows the existing local single-user trust model. Directory enumeration does not read file contents or modify monitored folders.
- Listings return up to 1000 sorted child directories; exact manual path entry remains available for larger folders.
