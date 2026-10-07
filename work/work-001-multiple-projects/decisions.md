# Work 001 Decisions

## 2026-10-08 — Local file registry
- Context: A single user needs persistent project selection without a database.
- Decision: Store versioned JSON using atomic replacement; one running WorkWeave process per registry. Canonical work paths prevent duplicate root/work aliases.
- Consequence: Monitored projects remain read-only; registry storage is separate. Corrupt registries fail visibly without overwriting data.

## 2026-10-08 — Navigation and compatibility
- Context: Startup must no longer assume a project.
- Decision: `/` is the project library; `/projects/<id>` renders a dashboard; `/api/projects` lists/adds; `/api/projects/<id>/workflow` returns state. Legacy `/api/workflow` and `/api/state` accept `?project=<id>` or the sole registered project, and reject ambiguous selection.
- Consequence: Explicit CLI target seeds the registry; exports continue defaulting to the current directory. Browser navigation uses stable project IDs.

## 2026-10-08 — Container access and local trust boundary
- Context: Browsers cannot grant arbitrary host-folder access to Docker.
- Decision: Mount one configurable parent at `/projects` read-only, enforce that boundary for registered paths, and store the registry at `/data`. Bind published ports to loopback. Require JSON and a custom same-origin header for writes; validate Host and Origin and remove wildcard CORS.
- Consequence: Users enter container-visible paths in Docker; native runs accept readable absolute local paths. This remains a trusted local single-user application without remote authentication.
