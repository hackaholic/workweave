# Work 004 — Modular architecture, templates and UI assets

## Objective
Separate HTTP handling, workflow operations, HTML rendering, CSS and browser behavior so each can evolve without editing giant Python strings. Preserve existing user flows and the lightweight local deployment.

## Status
Pending implementation. Planning and contracts are ready; this request does not start application refactoring.

## Architecture
Use a modular monolith with MVC-style layers: HTTP controllers call services; services use filesystem repositories and pure models; view renderers compose trusted templates; browser modules consume view data and APIs. Keep the Python standard-library runtime and existing CLI entry point. Do not add a database, web framework, SPA framework or Node build requirement.

- Fit: a single-user local application needs clear boundaries within one process.
- Tradeoff: more small files and explicit resource/rendering contracts instead of one-file generators.
- Maintainability: reuse shared UI primitives and tokens, test domain behavior separately from transport, and keep page changes out of filesystem code.

## Target blueprint

```text
workweave/
  cli.py                         # CLI/configuration entry point, including export mode
  config.py                      # normalized settings shared with server bootstrap
  models.py                      # existing workflow dataclasses, no I/O
  errors.py                      # domain errors; HTTP status mapping lives in controllers
  server.py                      # HTTPServer startup and handler composition
  controllers/
    projects.py                  # project and folder endpoints
    workflow.py                  # workflow state and write endpoints
    pages.py                     # HTML responses
    http.py                      # request validation, JSON/errors, safe asset responses
  services/
    projects.py                  # registration/browsing policies
    workflow.py                  # comments, subtasks, creation and scaffolding use cases
  repositories/
    projects.py                  # registry JSON persistence
    workflow.py                  # Markdown/JSON reads and writes
  parsing/
    markdown.py                  # pure extraction/checklist/contract helpers
  views/
    renderer.py                  # escaped context, explicit trusted-fragment composition
    pages.py                     # page-specific view models and render entry points
    export.py                    # same resources composed into standalone HTML
  templates/
    base.html
    projects.html
    dashboard.html
    error.html
    partials/
      project-navigation.html
      folder-picker.html
      contract-dialog.html
      comment-dialog.html
      work-dialog.html
  static/
    css/
      tokens.css                 # colors, typography, spacing, radii, layers
      base.css                   # reset, typography, focus and layout defaults
      components.css             # buttons, fields, cards, badges, dialogs
      projects.css               # library and folder picker layout
      dashboard.css              # metrics, filters, work list/detail layout
    js/
      core/api.js                # shared JSON client and error handling
      core/dom.js                # safe rendering and dialog helpers
      projects/library.js
      projects/folder-picker.js
      dashboard/state.js
      dashboard/render.js
      dashboard/actions.js
      dashboard/dialogs.js
      projects-page.js           # page initialization
      dashboard-page.js          # page initialization
  parser.py                      # compatibility facade during migration
  projects.py                    # compatibility facade during migration
  dashboard.py                   # preserve generate_html_dashboard public API
  project_ui.py                  # compatibility facade during migration
```

Folders describe responsibilities, not a requirement for empty abstractions. Use concrete functions/classes; no generic repository interfaces or dependency-injection framework. Final module splits may consolidate genuinely tiny helpers while preserving dependency direction.

## Dependency and rendering rules

- Flow: CLI/server → controllers → services → repositories/parsing/models. Views depend on models/view data and packaged resources, never on HTTP handlers. Lower layers must not import controllers or views.
- Use `importlib.resources` for packaged assets/templates and include them in wheel/sdist package data. Runtime must not rely on repository cwd.
- Prefer `string.Template` with explicit context and named partial composition; no custom template language, expression evaluation or user-selected template paths. Escape plain text/attributes by default; only renderer-created fragments are trusted HTML. Serialize page data as non-executable JSON with safe script-delimiter escaping.
- Use classic deferred scripts in explicit dependency order, small modules in one intentional namespace, and event listeners/data attributes. This permits the exact same script sources to be embedded in `file://` static exports without a bundler or module-fetch restrictions.
- CSS loads in tokens → base → components → page order. Use semantic classes and shared state classes/data attributes. Replace the external runtime Tailwind script with packaged CSS; preserve current appearance and responsive behavior. Limit inline styling to validated dynamic values such as numeric progress through a documented helper.
- Live pages reference static assets; export inlines those same CSS/JS sources. Offline exports retain search/filter/contract inspection but clearly disable server-write actions. No localhost fetches or CDN requirement when opening an export.

## Compatibility and scope

Preserve existing routes, JSON shapes, project IDs/registry format, workflow file formats, CLI flags, public imports and generator signatures. Cover project registration/switching, folder browsing, KPI filters, comments, subtask toggling/title edits/creation, draft/new work and scaffolding, contract dialogs, and exports. Reuse Work 001–003 implementations; do not redo their feature design.

Out of scope: new user features, visual rebranding, storage migrations, authentication, dependency upgrades, unrelated security redesign, or mass rewriting of monitored repositories. Newly discovered unsafe behavior is a finding, not an acceptance requirement to preserve: fix a narrow blocker with explicit tests or record a separate work item.

## Subtasks and dependencies

| Task | Role | Prerequisites | Deliverable |
| --- | --- | --- | --- |
| 004.1 | Backend engineer | None | Behavior baseline and separated models/services/repositories/controllers |
| 004.2 | Engineer | 004.1 | Safe templates, packaged static delivery and export composition |
| 004.3 | UI designer / engineer | 004.2 | Managed CSS tokens, reusable components and page styles |
| 004.4 | Frontend engineer | 004.2; integrate with 004.3 | Modular browser behavior and explicit page initialization |
| 004.5 | Test / review | 004.1–004.4 | Regression, offline export, wheel and Docker/browser verification |

## Done when
All five contracts satisfy their observable acceptance checks, behavior stays compatible, distribution includes all resources, offline exports work, and review/security evidence is recorded. Update project guidance to reflect the implemented module layout at completion.
