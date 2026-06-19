# Design — 0001 Foundation

## Shape

procurement-pattern-library is a directory of typed Markdown files
plus a small Python CLI for validation and retro rendering. The
patterns are the product; the CLI exists to keep them well-typed
and to roll them up quarterly.

The architecture has three layers:

1. **Patterns.** `patterns/<id>.md` is the unit. Each pattern has
   front-matter and a body.
2. **Cases.** `patterns/<id>/applications/<case-id>.md` is one
   application case. Each case has front-matter and a body.
3. **Retro.** `src/procurement_pattern_library/retro.py` reads the
   library and emits a quarterly Markdown report.

## File shapes

A pattern file:

```
---
id: dual-source
name: Dual-source the critical path
canonical_statement: When one node failing kills the whole flow, run
  two suppliers in parallel and pay the redundancy cost.
domains: [procurement, supply-chain, ai-build]
created_at: 2026-06-19
applications_dir: applications/
---

(body: longer discussion of the pattern, edge cases, anti-patterns)
```

A case file:

```
---
id: model-routing-fallback
pattern_id: dual-source
domain: ai-build
upstream_artifact: repo://athena-site/decisions/DEC-AS-042-model-fallback.md
opened_at: 2026-04-12
outcome: transferred-cleanly
---

(body: one-paragraph case description, what was learned)
```

## Validator behaviour

`validate_patterns.py` walks `patterns/`, parses each Markdown
file's front-matter, validates against the relevant schema, and
checks the `upstream_artifact` URI scheme is one of `repo://`,
`file://`, or `https://`. The validator does not de-reference the
URI; that is left to a future check.

`validate_outcomes.py` walks all cases and flags any older than
ninety days with an empty `outcome`.

## Retro renderer

`retro.py` reads every pattern and case, groups cases by quarter,
and emits a `retros/<quarter>.md` file. The retro lists:

- Top five patterns by case count this quarter
- Patterns with a rising `did-not-transfer` count
- Patterns with zero cases ever (candidates for retirement)
- New patterns added this quarter

The retro is mechanical. No LLM scoring in v0.

## Seed corpus shape

v0 seed patterns are extracted from the existing portfolio
decisions ledger. Candidates include:

- `dual-source` (procurement primitive; cross-applied to model
  routing fallback)
- `escalation-clause` (procurement primitive; cross-applied to
  reviewer escalation in ai-field-brief review queue)
- `capacity-reservation` (procurement primitive; cross-applied to
  eval-budget reservation in supplier-risk-rag-agent)

Each seed pattern carries at least two cases drawn from existing
DECs across the portfolio.

## Out of v0 scope

- LLM-generated pattern drafts
- A web docs site
- Cross-author contribution flow
- Auto-extraction of new patterns from the decisions ledger
