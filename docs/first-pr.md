# First PR

The literal first PR after this scaffold. The goal is the schemas,
three seed pattern files with two cases each, and the decision
record closing the domain enum.

## Files this PR adds

- `schemas/pattern.schema.json`
  - JSON Schema draft 2020-12
  - Required front-matter: `id`, `name`, `canonical_statement`,
    `domains[]`, `created_at`, `applications_dir`
  - `domains[]` enum: `procurement`, `supply-chain`,
    `mechanism-design`, `ai-build`
- `schemas/case.schema.json`
  - Required front-matter: `id`, `pattern_id`, `domain`,
    `upstream_artifact`, `opened_at`
  - Optional: `outcome` (enum: `transferred-cleanly`,
    `transferred-with-friction`, `did-not-transfer`,
    `still-pending`)
- `schemas/retro.schema.json`
  - Front-matter schema for the quarterly retro report
- `patterns/dual-source.md`
  - Canonical statement and body
  - `domains: [procurement, supply-chain, ai-build]`
- `patterns/dual-source/applications/lse-bauxite-2023.md`
  - Procurement-domain case from a past sourcing decision
- `patterns/dual-source/applications/model-routing-fallback.md`
  - ai-build-domain case pointing at an existing DEC in the
    portfolio
- `patterns/escalation-clause.md`
  - Canonical statement and body
- `patterns/escalation-clause/applications/`
  - Two cases: one procurement, one ai-build
- `patterns/capacity-reservation.md`
  - Canonical statement and body
- `patterns/capacity-reservation/applications/`
  - Two cases: one procurement, one ai-build
- `decisions/DEC-PPL-001-domain-closure-and-outcome-rule.md`
  - Justifies the four-domain enum
  - Justifies the ninety-day outcome rule
  - Lists domains considered and deferred (e.g., legal-contracts,
    sales-comp) with one-line reasons

## Verification

```
python -m pytest        # no tests yet; runner exits clean
python scripts/validate_schemas.py
python scripts/validate_patterns.py
```

Both exit zero. Every pattern file parses. Every case file parses.
Every `upstream_artifact` URI starts with `repo://`, `file://`,
or `https://`.

## What this PR does not do

- No outcome validator. PR 2 adds it.
- No retro renderer. PR 3 lands it.
- No CLI entry point.
- No voice-lint script. That lands in PR 2.
