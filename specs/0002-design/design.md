# Design — 0002 Control plane

The 0001 spec declared the data shapes. 0002 lands the runtime:
loader, validator, scorer, retro, CLI, packaging, and the first
ledger row.

## Package layout

```
procurement_pattern_library/
  __init__.py        # version, public re-exports
  __main__.py        # `python -m procurement_pattern_library`
  cli.py             # argparse, subcommand dispatch
  loader.py          # walk + YAML front-matter parser
  validator.py       # schema check + ninety-day rule
  score.py           # transfer index + ledger writer
  retro.py           # stdout markdown table over a ledger row
```

The package is laid out at the repo root (flat layout) so the
factory contract gate, which expects
`procurement_pattern_library/<module>.py`, picks the modules up
directly. `hatchling` is configured to package exactly
`procurement_pattern_library`.

## Loader

The loader has two public functions:

- `load_corpus(root: Path) -> Corpus` — walks `root/patterns/`,
  returns a `Corpus` carrying a list of `Pattern` and a list of
  `Case`. The corpus does not de-duplicate; the validator handles
  duplicate-id reporting.
- `parse_front_matter(text: str) -> tuple[dict, str]` — splits a
  Markdown file into `(front_matter_dict, body)`. Reused by
  scripts under `scripts/`.

`Pattern` and `Case` are dataclasses, not dicts. The loader does
not validate the schema; it only parses YAML. Schema enforcement
is the validator's job, kept separate so the loader can be used
by tools that want to surface partial corpora (for example, the
voice-lint gate).

## Validator

The validator has one public function:

- `validate(corpus: Corpus, schemas: SchemaSet, today: date) ->
  ValidationResult` — returns a list of `ValidationIssue` records
  carrying a severity, a file path, and a message.

Severity is one of `error` or `warning`. The CLI exits non-zero
if any `error` issues are present. `warning` issues are printed
but do not fail the gate.

Schema enforcement is hand-rolled, not `jsonschema`-driven. The
required-field check, enum-membership check, and URI-prefix check
are written out long-hand. This keeps the dev dep set small for
v0.1; switching to `jsonschema` is in the queue.

## Scorer

The scorer has two public functions:

- `score_quarter(corpus: Corpus, quarter: str, weights:
  ScoreWeights, today: date) -> RunResult` — returns a
  `RunResult` carrying per-pattern scores, input counts, and the
  weights used.
- `write_ledger_row(result: RunResult, out_dir: Path) -> Path` —
  writes the ledger row as YAML front-matter plus a short body.
  The filename is derived from `result.run_id`.

`ScoreWeights` is a dataclass with one field today,
`friction_weight: float = 0.5`. Future weights (for example,
recency decay) will land as fields here and as columns in the
ledger row.

## Retro

The retro renderer takes a parsed ledger row and prints a
Markdown table to stdout sorted by transfer index. v0.1 does not
persist; `--out` is a flag stub that warns and is ignored. The
write-to-file path lands in spec 0003 to keep the v0.1 surface
small.

## CLI

```
python -m procurement_pattern_library validate
python -m procurement_pattern_library score --quarter 2026-Q2
python -m procurement_pattern_library retro --quarter 2026-Q2
```

Each subcommand accepts a `--root` flag defaulting to the current
working directory. The CLI dispatches to the layer functions
above and converts exceptions into non-zero exit codes with a
single-line error message.

## Tests

`tests/conftest.py` constructs a tiny in-tree corpus fixture
under `tests/fixtures/` so the suite does not depend on the
checked-in seed patterns. Each layer is tested in isolation:

- `tests/test_loader.py` — front-matter parsing, body separation,
  pattern-id mismatch rejection.
- `tests/test_validator.py` — schema enforcement, the ninety-day
  rule, duplicate-id reporting.
- `tests/test_score.py` — transfer-index math, friction weight,
  strict-index gap, ledger-row determinism.
- `tests/test_cli.py` — subprocess smoke test of `validate`.

## Ledger row format

A ledger row is a Markdown file with YAML front-matter:

```
---
run_id: 2026-Q2-transfer-score
generated_at: 2026-06-22
quarter: 2026-Q2
friction_weight: 0.5
inputs:
  patterns: 3
  cases: 6
scores:
  - pattern_id: dual-source
    case_count: 2
    transfer_index: 1.0
    strict_index: 1.0
    outcomes:
      transferred-cleanly: 2
  - ...
---

(short body describing the run, any notable shifts vs the
previous row, and any calibration notes)
```

The row is a checked-in artifact; the writer is deterministic so
the diff between rows is meaningful.

## Out of 0002 scope

- Persisting the retro to `retros/<quarter>.md`. Spec 0003.
- Voice-lint as a failing gate. Spec 0003.
- `jsonschema`-driven validation. Future cleanup spec.
- URI de-referencing. Future cleanup spec.
