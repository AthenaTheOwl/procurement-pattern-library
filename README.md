# procurement-pattern-library

A bauxite supplier fed one LSE contract for three years. A routine audit found the supplier was itself single-sourced from one mine. The fix was a second contract at a fifteen-percent volume share — and two years later the same shape showed up again, as a fallback model kept warm by five percent of traffic when the primary endpoint went dark for ninety minutes. Same pattern. Different decade, different commodity. This library writes the pattern down once and tracks both ends.

## What it does

Each pattern is a file. It names a principle from the procurement, supply-chain, or mechanism-design world — dual-source the critical path, escalation clause for asymmetric exceptions, capacity reservation against contention windows — sketches the canonical procurement case, and then carries a typed list of application cases where the same principle resurfaced in an AI build.

The two-way reading is the point. Designing a new system: which day-job patterns apply here? Mid-negotiation: which AI-build case sharpens the intuition? Every application case carries an `outcome` field — `transferred-cleanly`, `transferred-with-friction`, `still-pending` — filled in ninety days after the case opened, so a quarterly score can say which patterns actually transferred and which only looked like they would.

v0.1 ships three seed patterns and five application cases, all of them scored. The corpus is small on purpose. The "rising did-not-transfer" signal needs roughly fifteen patterns before it means anything; until then the scorer is honest about working off a thin panel.

## Try it

The quickest look at the corpus. Reads the committed files, ranks patterns by transfer signal, offline:

```
python -m procurement_pattern_library show
```

```
procurement pattern library - transfer signal across the corpus
==============================================================

3 pattern(s), 6 application case(s) (5 scored, 1 pending).

   #  pattern                                          cases  transfer  strict
  ----------------------------------------------------------------------------
   1  Escalation clause for asymmetric exceptions          2      1.00    1.00
   2  Capacity reservation against contention windows      2      0.75    0.50
   3  Dual-source the critical path                        2      0.75    0.50

headline: `escalation-clause` leads at transfer index 1.00 over 2 case(s).
```

`transfer` counts a friction transfer as half a clean one; `strict` counts it as zero. The gap between the two columns is where a pattern claimed it transferred but charged an integration tax to do it.

The rest of the verbs:

```
python -m procurement_pattern_library validate
python -m procurement_pattern_library score --quarter 2026-Q2 --no-write
python -m procurement_pattern_library retro --quarter 2026-Q2
```

- `validate` parses every pattern and case file against the schema and flags any case older than ninety days whose outcome is still empty or `still-pending`.
- `score` computes the per-pattern transfer index for one quarter and writes a ledger row (`--no-write` prints instead).
- `retro` prints a Markdown retro for the quarter.

Run the tests with `python -m uv run pytest -q`.

## Live demo

A Streamlit card-browser over the same corpus the `show` verb reads — the ranked transfer table, a friction-weight slider, and a per-pattern drill-down into its application cases. It reads the committed files; no network, no keys.

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Deploy on Streamlit Community Cloud: repo `AthenaTheOwl/procurement-pattern-library`,
branch `main`, main file `streamlit_app.py`.

<!-- live url: (paste the Streamlit Cloud URL here once deployed) -->

## How it connects

The application cases point at where each pattern got re-applied. Those are real repos, and the links survive:

- [athena-site](https://github.com/AthenaTheOwl/athena-site) — the model-routing fallback that mirrors the bauxite dual-source, friction and all.
- [supplier-risk-rag-agent](https://github.com/AthenaTheOwl/supplier-risk-rag-agent) — the eval-budget reservation that bought token capacity ahead of the contention window.
- [negotiation-mechanism-replay](https://github.com/AthenaTheOwl/negotiation-mechanism-replay) — the mechanism-design neighbor: same procurement primitives, replayed as bargaining games.

Not every `upstream_artifact` resolves from the public portfolio. The three procurement-side cases (`lse-bauxite-2023`, `long-tail-vendor-2024`, `q4-warehouse-prebook-2025`) cite `repo://decisions-ledger/...`, a decisions ledger that is not in the public portfolio; treat those references as private, external provenance that a public checkout cannot resolve. The decision files the two ai-build cases cite (`DEC-AS-042`, `DEC-SRRA-022`) are not present in the public athena-site and supplier-risk-rag-agent repos as of 2026-10-20; the repo links above resolve, those file paths do not. A third ai-build case, `reviewer-escalation-ai-field-brief`, was retired on 2026-10-20: it passed the ninety-day window still pending, and the decision and review queue it described (`DEC-AFB-017`) were never built in ai-field-brief, so there was no outcome to measure.

## Layout

```
procurement_pattern_library/    package: cli, loader, validator, scorer, retro, show
patterns/<id>.md                one file per pattern
patterns/<id>/applications/     typed application cases, one per file
schemas/                        pattern, case, retro front-matter schemas
ledger/runs/                    the checked-in transfer-score rows
specs/  tests/  docs/  decisions/
```

## Method update

[October method update: Test a transfer before learning its outcome](docs/prospective-transfer-review.md).

## License

MIT. See [LICENSE](LICENSE).
