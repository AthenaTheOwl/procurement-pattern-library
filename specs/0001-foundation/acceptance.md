# Acceptance — 0001 Foundation

"v0 done" means the following hold simultaneously.

## Artifacts present

- `schemas/pattern.schema.json` validates
- `schemas/case.schema.json` validates
- `schemas/retro.schema.json` validates
- At least three pattern files under `patterns/<id>.md`, each with
  at least two cases in `patterns/<id>/applications/`
- `decisions/DEC-PPL-001-domain-closure-and-outcome-rule.md`
  exists

## Gates pass

Run from the repo root:

```
python -m pytest
python scripts/voice_lint.py
python scripts/validate_schemas.py
python scripts/validate_patterns.py
python scripts/validate_outcomes.py
python scripts/validate_decisions.py
```

All six exit zero.

## CLI smoke

```
python -m procurement_pattern_library validate
```

Exits zero. The CLI prints a per-pattern summary noting the case
count.

## Manual review

- A reader can pick any pattern file and find at least two cases
  with non-empty bodies, each pointing at a real upstream artifact
  URI.
- The DEC justifies the four-domain enum closure and the ninety-
  day outcome rule.
- No pattern uses marketing language in its canonical statement.

## Out of v0 acceptance

- The retro renderer ships as a skeleton in spec 0001 and is
  fully wired in PR 3. The first checked-in retro may be empty
  or hand-curated.
- Auto-extraction of patterns from the decisions ledger is spec
  0003.
- Cross-pattern relationships (pattern A is a refinement of
  pattern B) are spec 0004.
