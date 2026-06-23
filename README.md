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


v0.1 shipped — runnable, minimal. The CLI ships `show`, `validate`,
`score`, and `retro`; a Streamlit app browses the corpus (see
[live demo](#live-demo)). The next passes deepen it (more patterns,
real-data backfill). See `specs/` for scope and `STATUS.md` for the
current state and next-feature queue.

## How to run

The CLI ships four verbs. The quickest look at the corpus:

```
python -m procurement_pattern_library show
```

`show` reads the committed corpus and prints a ranked transfer-signal
table (one row per pattern, best-first) plus a one-line headline
finding. Read-only, offline.

The rest:

```
python -m procurement_pattern_library validate
python -m procurement_pattern_library score --quarter 2026-Q2 --no-write
python -m procurement_pattern_library retro --quarter 2026-Q2
```

- `validate` parses every pattern + case file and checks it against the
  schema and the outcome rule.
- `score` computes the per-pattern transfer index for one quarter and
  writes a ledger row (use `--no-write` to print instead).
- `retro` prints a Markdown retro for a quarter.

Run the tests with `python -m uv run pytest -q`.

## live demo

A Streamlit card-browser over the same corpus the `show` verb reads —
a ranked transfer table, a friction-weight slider, and a per-pattern
drill-down into its application cases.

Run it locally:

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: repo `AthenaTheOwl/procurement-pattern-library`,
branch `main`, main file `streamlit_app.py`.

<!-- live url: (paste the Streamlit Cloud URL here once deployed) -->

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
