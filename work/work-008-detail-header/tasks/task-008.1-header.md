# Task 008.1 — Responsive detail header

**Owner:** Codex
**Status:** Completed

## Scope
Header CSS and markup only; preserve navigation and workflow behavior.

## Acceptance
- [x] Long title wraps; review action and badges do not overlap at desktop and narrow widths.
- [x] Keyboard focus remains visible; browser and build checks pass.

## Security
Preserve escaped title and existing encoded links. No new data writes or dependencies.

## Verification
- Python compileall and git diff --check passed.
- Docker Compose rebuild completed; service healthy and updated CSS served.
- Browser checked at 1280px and 390px: title wraps at narrow width, controls remain below it, no header horizontal overflow. Keyboard focus ring visible.
- Scoped review: title escaping and review links unchanged; no new writes or dependencies.
