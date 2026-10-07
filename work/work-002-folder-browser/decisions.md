# Work 002 Decisions

## 2026-10-08 — Server-visible folder picker
- Context: WorkWeave runs in Docker and needs persistent paths to mounted folders, not uploaded copies.
- Decision: Provide an in-app directory picker using the existing local API trust boundary and project-root restriction. Canonicalize paths and omit symlink entries that escape the root. Only return directory names/paths, not file contents.
- Consequence: Docker browses `/projects`; native runs start at home. Keep manual input as an alternative. Selecting a valid folder fills the form; Add project remains the registration action.

## 2026-10-08 — Bounded listings and async state
- Context: Large folders and rapid navigation should not produce unusable responses or stale selections.
- Decision: Return at most 1000 sorted directories and report truncation. Cancel superseded requests and disable selection until a successful current response confirms a valid project.
- Consequence: Unusually large listings can use manual path input. Errors offer retry and navigation back to the starting folder.
