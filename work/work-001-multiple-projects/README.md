# Work 001 — Multiple projects and UI onboarding

## Objective
Start WorkWeave with an empty project library, add local projects in the UI, persist them across restarts, and navigate each project's workflow dashboard.

## Architecture
A standard-library JSON registry stores project IDs, names and canonical work-directory paths outside monitored repositories. The home page lists projects and provides an add form. Project-specific URLs select dashboards and JSON state. Docker exposes a configurable parent directory read-only and persists registry data in a named volume.

## Scope
Include onboarding, add/list/select, validation, persistence, CLI compatibility, Docker configuration and tests. Exclude comments, task editing, project deletion, authentication, and a database.

## Done when
The contract's acceptance checks pass, browser behavior is verified, and self-review findings are resolved or documented.

## Status
Completed. Verification and local preview details are recorded in notes.md.
