# Requirements — 0002 Design

Spec 0002 records what the v0.1 control-plane PR added on top of
the 0001 scaffold. The R-PPL-* numbering continues from 0001.

## CLI and packaging

- **R-PPL-011** The package is named `procurement_pattern_library`
  and is importable as such from a uv-managed venv. The package
  ships under `src/`.
- **R-PPL-012** `pyproject.toml` declares dev dependencies under
  `[dependency-groups]` and sets `[tool.uv] package = true` so
  `python -m uv sync` installs the package editable into the
  venv. The build backend is hatchling.
- **R-PPL-013** The CLI exposes three subcommands: `validate`,
  `score`, `retro`. The entry point is `python -m
  procurement_pattern_library`. Each subcommand returns a process
  exit code of zero on success.

## Loader

- **R-PPL-014** `loader.py` walks `patterns/` recursively and
  yields parsed pattern objects and case objects. A pattern file
  is recognized by being directly under `patterns/` and having a
  YAML front-matter block.
- **R-PPL-015** A case file is recognized by being under
  `patterns/<pattern-id>/applications/` and having a YAML front-
  matter block. The loader rejects any case whose declared
  `pattern_id` does not match the directory it lives in.
- **R-PPL-016** The loader is tolerant of trailing whitespace and
  blank lines around the front-matter block but rejects front-
  matter that is missing either fence.

## Validator

- **R-PPL-017** `validator.py` checks every pattern and case
  against the schemas under `schemas/` and applies the ninety-
  day outcome rule from R-PPL-007.
- **R-PPL-018** The validator returns a structured result listing
  per-file errors and warnings. The CLI `validate` subcommand
  prints them in a human-readable form and exits non-zero if any
  error is present.

## Scorer

- **R-PPL-019** `score.py` computes a per-pattern transfer index
  over a target quarter. The methodology is recorded in
  `docs/methodology.md`; the implementation must match the doc.
- **R-PPL-020** Every scoring run writes a ledger row at
  `ledger/runs/<run-id>.md` containing the input counts, the
  weights used, the per-pattern scores, and the run timestamp.
  Re-running the same scoring command on the same corpus must
  produce the same row except for the timestamp.
- **R-PPL-021** The first scoring run, `ledger/runs/2026-Q2-
  transfer-score.md`, is checked in to anchor downstream
  comparisons.

## Tests

- **R-PPL-022** `tests/` contains coverage for the loader,
  validator, and scorer. The test suite runs under `python -m
  pytest` from the repo root and exits zero.
- **R-PPL-023** A CLI smoke test invokes `python -m
  procurement_pattern_library validate` as a subprocess and
  asserts a zero exit code.

## Docs

- **R-PPL-024** `docs/product-brief.md`, `docs/system-map.md`,
  and `docs/methodology.md` are checked in and describe the
  library's purpose, the data flow, and the scoring rules
  respectively. The methodology doc and `score.py` must agree.

## Status

- **R-PPL-025** `STATUS.md` lives at the repo root and has the
  three H2 sections `## Current state`, `## Known limits`, and
  `## Next feature queue`. The headings are load-bearing for
  the factory contract gate.
