# Acceptance — 0002 Control plane

"Spec 0002 done" means the following hold simultaneously.

## Files present

- `pyproject.toml` declaring `[dependency-groups]` and `[tool.uv]
  package = true`.
- `src/procurement_pattern_library/` with `__init__.py`,
  `__main__.py`, `cli.py`, `loader.py`, `validator.py`,
  `score.py`, `retro.py`.
- `schemas/pattern.schema.json`, `schemas/case.schema.json`,
  `schemas/retro.schema.json`.
- Three pattern files under `patterns/` each with two cases.
- `decisions/DEC-PPL-001-domain-closure-and-outcome-rule.md`.
- `ledger/runs/2026-Q2-transfer-score.md`.
- `tests/` with loader, validator, scorer, and CLI tests.
- `docs/product-brief.md`, `docs/system-map.md`,
  `docs/methodology.md`.
- `STATUS.md` with the three load-bearing H2 sections.

## Gates pass

Run from the repo root, in a uv-managed venv:

```
python -m uv sync
python -m uv run pytest
python -m uv run python -m procurement_pattern_library validate
python -m uv run python -m procurement_pattern_library score --quarter 2026-Q2
python -m uv run python -m procurement_pattern_library retro --quarter 2026-Q2
```

All five exit zero.

## Manual review

- The ledger row matches the methodology: weights line up, score
  formula lines up, per-pattern outcome counts match the seed
  cases.
- The system map's data flow agrees with the layer functions in
  the source.
- The product brief is the only doc a contributor needs to read
  to know what is in scope.

## Out of 0002 acceptance

- Persisted retro reports. Spec 0003.
- Calibrated friction weight. DEC-PPL-002.
- Voice-lint as a failing gate. Spec 0003.
