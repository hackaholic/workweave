# Task 10.1 — Read and display task objectives

**Task ID:** 10.1
**Owner:** Codex
**Status:** Completed

## Objective
Read canonical and observed combined objective headings; expose missing-objective warnings in contract cards and modal.

## Scope
Parser compatibility helper, dashboard warnings, tests and local documentation. No source migrations or shared skill edits.

## Dependencies
- Depends on: None
- Blocked by: None

## Test cases
- TC01 canonical and five observed aliases return full paragraph text and stop before next section.
- TC02 absent/empty/unrecognized objective emits actionable warning, without guessing.
- TC03 parsing preserves original file bytes, including HTML-like objective text; UI retains escaping.
- TC04 full suite and local Work018 browser contract verification.

## Security validation
Read-only parsing; keep existing HTML escaping. No API/permission changes.

## Acceptance checks
- [x] Regression tests pass and Work018 objectives display.
- [x] Missing objectives visibly warn; source history unchanged.
- [x] Local self-review and verification recorded.

## Verification
TC01–TC03 pass in regression suite; TC04 full suite 51/51 and rebuilt local browser Work018 cards/modal verified. Security self-review passed; original source bytes preserved. See notes.md.
