# Procurement Pattern Library

Typed library of supply-chain, negotiation, and mechanism-design patterns (dual-source, escalation clause, capacity reservation, RFQ scoring) with bi-directional links to how each has been re-applied in an AI build (model dual-source, fallback routing, eval-budget reservation).

## What this is

A typed Markdown library where each pattern is a file. A pattern names
a principle from the procurement / supply-chain / mechanism-design
world, sketches the canonical procurement application, and then carries
a growing list of cross-applications: cases where the same principle
showed up in an AI build.

The pattern is the unit. Each pattern file has a structured front-
matter block, a body, and a typed `applications/` subdirectory holding
one application case per file. Each case carries an `outcome` field
filled in ninety days after the case was opened.

The two-way reading is the point:

- Designing a new AI system: which day-job patterns apply here?
- In a procurement negotiation: which AI-build cases sharpen my
  intuition about this class of problem?

## Who uses it

The user (Vignesh), as a personal-knowledge primitive. Outside readers
who want to see how patterns transfer between the procurement and AI
worlds. Eventually: a typed corpus that a mechanism-design assistant
can ground on.

## Why now

The portfolio's CDCP operating model already names cross-domain
transfer as the leverage axis. The decisions ledger has implicit
cross-applications scattered through it. This repo extracts those
into a typed library so a quarterly retrospective can score which
patterns actually transferred.

## Status

v0 scaffold; no implementation yet. The specs ledger names the first
set of requirements (R-PPL-001 through R-PPL-010). The first PR after
this scaffold lands the pattern schema and the first three patterns
extracted from the existing decisions ledger.

## How to run

Placeholder; will land in spec 0002. v0 ships the schema, the first
three patterns, and a validator that confirms every pattern file is
well-typed. No runtime is required to read the library.

The eventual CLI shape (target for spec 0003):

```
python -m procurement_pattern_library validate
python -m procurement_pattern_library retro --quarter 2026-Q3 --out retros/2026-Q3.md
```

## Layout

```
procurement-pattern-library/
  README.md
  LICENSE
  AGENTS.md
  .gitignore
  specs/
    0001-foundation/
      requirements.md
      design.md
      tasks.md
      acceptance.md
  docs/
    first-pr.md
```

Future directories (named in specs, not created yet):

- `patterns/<pattern-id>.md` — one file per pattern
- `patterns/<pattern-id>/applications/<case-id>.md` — typed cases
- `schemas/` — pattern, case, retro schemas
- `retros/<quarter>.md` — quarterly retrospective reports
- `src/procurement_pattern_library/` — validator and retro runner

## License

MIT. See [LICENSE](LICENSE).
