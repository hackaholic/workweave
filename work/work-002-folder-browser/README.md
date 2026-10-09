# Work 002 — Browse and select project folders

## Objective
Let users browse directories and select a valid project without typing its path.

## Architecture
A read-only `/api/folders?path=...` endpoint lists child directories, parent navigation and whether the current folder is a valid project. A modal folder picker fills the existing Add project form. Docker browsing stays inside the configured projects root; native browsing starts at the user's home directory and supports filesystem navigation.

## Scope
Include folder browsing, selection, loading/error/empty states, keyboard support, boundary tests and Docker/browser verification. No file uploads, filesystem writes, native OS dialogs, or automatic project registration on selection.

## Status
Completed. See notes.md for verification evidence.
