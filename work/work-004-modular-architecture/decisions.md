# Work 004 Decisions

## 2026-10-09 — Modular monolith with MVC-style boundaries
- Context: Dashboard markup/style/behavior share a 975-line Python generator; the 768-line parser also performs workflow mutations. Project pages duplicate UI conventions.
- Decision: Separate concrete controllers, services, repositories, models, templates and static assets within the existing Python package.
- Consequence: More focused files; no additional deployment process, database, framework or generic abstraction layer.

## 2026-10-09 — Explicit templates and shared export resources
- Context: Dynamic server pages and standalone HTML export must both continue working after extraction.
- Decision: Use standard-library resource loading and explicit escaped template contexts/partials; live responses link packaged assets, while exports inline the same sources. Classic deferred scripts avoid file-origin ES-module fetch requirements.
- Consequence: Packaging, escaping, script ordering and read-only export behavior require direct acceptance tests. A full template engine can be reconsidered only if real complexity justifies it.

## 2026-10-09 — Managed CSS instead of runtime utility generation
- Context: Dashboard styling uses an external Tailwind runtime; project library styling is a Python string with separate values.
- Decision: Centralize semantic tokens and reusable component styles, then add scoped page styles and remove the CDN script once parity is verified.
- Consequence: No network/build requirement for styling. Preserve recognizable appearance; compare desktop/mobile states rather than treating a redesign as part of extraction.

## 2026-10-09 — Incremental migration and compatibility facades
- Context: CLI exports, tests and callers import the current modules directly.
- Decision: Keep public facades/signatures while moving implementation; use existing JSON/file formats and API contracts. Each migration stage must remain runnable.
- Consequence: Temporary forwarding modules are acceptable; there must be one implementation of each behavior, not two divergent code paths.
