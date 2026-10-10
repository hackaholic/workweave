# Evidence
Work018 uses Objective and context in five contracts; exact-match parser dropped these descriptions.

Regression tests first reproduced eight failures (five aliases and three missing/empty/unsupported cases); both tests pass after fix. Full suite: 51 tests passed. Compileall and git diff --check pass.

Read-only scan of 107 Crochet contracts: missing parsed objectives decreased from 38 to 7; all six Work018 contracts now have objectives. Remaining seven use Requirement-only or no objective headings; warnings deliberately avoid inventing descriptions.

Local self-review: bounded alias recognition in workflow_format.py, existing parser section boundaries retained, cards/modal continue escaping objectives and warnings. Tests verify source bytes unchanged. No new trust boundary, dependencies, migrations, or monitored-project changes. Work009 belongs to separate existing work and is untouched.

Docker rebuild/restart succeeded. Browser confirmed all six Work018 card objectives and full Task18.5 modal text. Screenshot: /tmp/workweave-objective-fixed.png. Shared skills unchanged; local README specifies canonical headings.
