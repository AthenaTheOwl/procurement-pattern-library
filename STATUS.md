# STATUS — procurement-pattern-library

Snapshot of where the library and its tooling stand at the end of
the v0.1 control-plane PR. Section headings below are load-bearing:
the factory contract gate matches the literal strings `## Current
state`, `## Known limits`, and `## Next feature queue`.

## Current state

- Three seed patterns are checked in: `dual-source`,
  `escalation-clause`, `capacity-reservation`. Each carries two
  typed application cases (one procurement, one ai-build).
- Schemas for pattern, case, and retro front-matter live under
  `schemas/` and are loaded by the validator at startup.
- The Python CLI is runnable via `python -m
  procurement_pattern_library` with three subcommands: `validate`,
  `score`, `retro`.
- `validate` walks `patterns/` and `decisions/`, parses every
  Markdown file's front-matter, checks it against the schema, and
  flags any application case older than ninety days with an empty
  outcome. Exits zero on the seed corpus.
- `score` computes a per-pattern transfer index over a named
  quarter and writes a structured ledger row at
  `ledger/runs/<run-id>.md`. The first row,
  `ledger/runs/2026-Q2-transfer-score.md`, is checked in and is
  the record of the first scoring run.
- `retro` is a thin renderer over the score output. v0.1 prints
  the per-pattern table to stdout; persisting `retros/<q>.md` is
  spec-0003 scope.
- Tests under `tests/` cover the loader, the validator, and the
  scorer. The CLI is smoke-tested through `python -m
  procurement_pattern_library validate` in a pytest fixture.
- `pyproject.toml` declares dev deps under `[dependency-groups]`
  and sets `[tool.uv] package = true` so the project installs
  editable into the uv-managed venv. The build backend is
  hatchling.
- Methodology, product brief, and system map are written down
  under `docs/` so a reader can audit the scoring logic without
  reading source.

## Known limits

- The retro renderer prints to stdout only. Writing the rendered
  Markdown report to `retros/<quarter>.md` is deferred to spec
  0003.
- The validator confirms the `upstream_artifact` URI scheme but
  does not de-reference the URI. A broken or moved DEC link will
  not be caught.
- The voice-lint script is a skeleton: it loads a banned-word
  list but only warns; it does not fail the gate. Hardening it
  into a CI gate is queued.
- Only three patterns are seeded. The library is too small for
  the retro's "rising did-not-transfer" signal to be meaningful;
  that signal becomes useful around fifteen patterns.
- The scoring methodology weights `transferred-with-friction` at
  0.5 of a clean transfer. This is a defensible default but has
  not been calibrated against a ground-truth panel.
- No JSON-Schema runtime validation library is used; the
  validator hand-checks required fields against the schema. A
  switch to `jsonschema` is a candidate cleanup.

## Next feature queue

- Wire the retro renderer end-to-end: render to
  `retros/<quarter>.md` from a Jinja template, link each pattern
  row back to its file, and check the first generated retro
  into the repo.
- Add `scripts/voice_lint.py` as a failing gate over
  `patterns/**/*.md` and `retros/*.md`, with the banned-word set
  declared in `BANNED_FAIL` and a separate `BANNED_WARN` set.
- Seed five more patterns from the existing portfolio decisions
  ledger so the rising-did-not-transfer signal becomes useful.
- Switch the validator from hand-rolled field checks to
  `jsonschema`-driven validation; keep the human-readable error
  formatting.
- Calibrate the `transferred-with-friction` weight: pick ten
  past cases, score them by hand, fit the weight to minimize
  divergence, record the result in a DEC-PPL.
- Add `scripts/validate_outcomes.py` as a standalone gate
  invokable from CI, separate from the in-process validator.
- Add a `--strict` mode to `validate` that fails on any URI that
  cannot be resolved (de-references `repo://` against a sibling
  checkout).

- Resolve factory defect: missing PRODUCT_BRIEF.md,SYSTEM_MAP.md
- Resolve factory defect: missing data/ledger/*.jsonl
- Resolve factory defect: METHODOLOGY.md missing revisit section
- Resolve factory defect: PRODUCT_BRIEF.md is required for active repos
- Resolve factory defect: SYSTEM_MAP.md is required for active repos
- Resolve factory defect: expected file 'PRODUCT_BRIEF.md' is missing
- Resolve factory defect: expected file 'SYSTEM_MAP.md' is missing
- Resolve factory defect: expected file 'procurement_pattern_library/cli.py' is missing
- Resolve factory defect: expected file 'procurement_pattern_library/score.py' is missing
- Resolve factory defect: expected file 'procurement_pattern_library/ledger.py' is missing
- Resolve factory defect: expected glob 'data/ledger/*.jsonl' matched no files
- Resolve factory defect: module 'cli' declares source 'procurement_pattern_library/cli.py', but it is missing
- Resolve factory defect: module 'score' declares source 'procurement_pattern_library/score.py', but it is missing
- Resolve factory defect: module 'ledger' declares source 'procurement_pattern_library/ledger.py', but it is missing
- Resolve factory defect: module 'report' declares source 'procurement_pattern_library/report.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
- Resolve factory defect: expected file 'procurement_pattern_library/cli.py' is missing
- Resolve factory defect: expected file 'procurement_pattern_library/score.py' is missing
- Resolve factory defect: expected file 'procurement_pattern_library/ledger.py' is missing
- Resolve factory defect: module 'cli' declares source 'procurement_pattern_library/cli.py', but it is missing
- Resolve factory defect: module 'score' declares source 'procurement_pattern_library/score.py', but it is missing
- Resolve factory defect: module 'ledger' declares source 'procurement_pattern_library/ledger.py', but it is missing
- Resolve factory defect: module 'report' declares source 'procurement_pattern_library/report.py', but it is missing
- Resolve factory defect: claude_code review requested patch; inspect defect log
