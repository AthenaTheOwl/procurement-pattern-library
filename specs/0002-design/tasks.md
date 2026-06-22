# Tasks — 0002 Control plane

Checkbox tasks for the v0.1 PR. All boxes are checked at the
time of this commit; the file stays in the repo as the audit
trail for the spec.

## Packaging

- [x] Add `pyproject.toml` with hatchling backend
- [x] Move package to `src/procurement_pattern_library/`
- [x] Declare dev deps under `[dependency-groups]`
- [x] Set `[tool.uv] package = true`

## Schemas

- [x] Author `schemas/pattern.schema.json`
- [x] Author `schemas/case.schema.json`
- [x] Author `schemas/retro.schema.json`

## Loader

- [x] Implement front-matter parser
- [x] Implement corpus walker
- [x] Reject case files whose `pattern_id` does not match the
      directory

## Validator

- [x] Schema enforcement
- [x] Ninety-day outcome rule
- [x] Duplicate-id reporting

## Scorer

- [x] Quarter window filter
- [x] Transfer-index computation
- [x] Strict-index computation
- [x] Ledger-row writer with deterministic output

## Retro

- [x] Stdout markdown table sorted by transfer index

## CLI

- [x] Argparse entry point with three subcommands
- [x] `python -m procurement_pattern_library` shim

## Seed corpus

- [x] `patterns/dual-source.md` with two cases
- [x] `patterns/escalation-clause.md` with two cases
- [x] `patterns/capacity-reservation.md` with two cases

## Decisions

- [x] `decisions/DEC-PPL-001-domain-closure-and-outcome-rule.md`

## Ledger

- [x] First scoring run at
      `ledger/runs/2026-Q2-transfer-score.md`

## Tests

- [x] Loader tests
- [x] Validator tests
- [x] Scorer tests
- [x] CLI smoke test

## Docs

- [x] Product brief
- [x] System map
- [x] Methodology
- [x] STATUS.md with the three required sections
