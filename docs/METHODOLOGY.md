# Methodology — pattern scoring and calibration

What the `score` subcommand computes, why it is computed that way, and
what its limits are. This is the doc to update when the scoring
weights or the rule set change; the implementation in
`src/procurement_pattern_library/score.py` mirrors what is written
here.

## Inputs

- The typed corpus: every pattern file and every application case
  file the loader can parse.
- A target quarter, expressed as `YYYY-Qn` (for example, `2026-Q2`).
  The scorer filters cases by `opened_at` falling inside the quarter
  window.
- The current date, used to apply the ninety-day outcome rule on
  cases that opened before the quarter window closed.

## Outcome enum

Every case carries an `outcome` field once the ninety-day window has
elapsed. The enum has four members:

| Outcome | Meaning | Weight |
|---|---|---|
| `transferred-cleanly` | Pattern applied without modification and worked | 1.0 |
| `transferred-with-friction` | Pattern applied but required non-trivial adaptation | 0.5 |
| `did-not-transfer` | Pattern was tried and abandoned | 0.0 |
| `still-pending` | Outcome not yet observable | excluded from numerator and denominator |

The weights were chosen to keep the metric within `[0, 1]` and to let
a friction case still count as partial credit. The 0.5 weight on
friction is the calibration target; see the Calibration section
below.

## Transfer index

For each pattern in the quarter window, the scorer computes:

```
transfer_index = sum(weight(c.outcome) for c in scored_cases)
                / len(scored_cases)
```

where `scored_cases` is the subset of the pattern's cases whose
`opened_at` falls in the quarter and whose `outcome` is not
`still-pending`. Patterns with zero scored cases have a
`transfer_index` of `null` and are surfaced as "no signal" in the
retro.

The score is intentionally not a count. A pattern with one clean
transfer and a pattern with ten clean transfers have the same transfer
index. The retro layer adds case-count as a tiebreaker so a
high-volume pattern is read before a low-volume one.

## Friction-adjusted vs. strict score

The scorer also computes a `strict_index`:

```
strict_index = count(c.outcome == 'transferred-cleanly')
             / len(scored_cases)
```

Both are written to the ledger row so a reader can compare. A large
gap between `transfer_index` and `strict_index` flags a pattern that
"sort of works" — many cases ended in friction rather than clean
transfer. That is a signal to refine the pattern statement or to
consider a sibling pattern.

## Ninety-day outcome rule

A case is added to the library the day a transfer is attempted. Its
`outcome` is left empty initially. After ninety days the outcome must
be filled in or the validator fails the gate. The ninety-day window
was picked because it is long enough for most AI-build cases to either
land or be quietly abandoned, and short enough that the library does
not accumulate ambiguous rows.

The validator reads `opened_at`, compares to today, and fails if the
difference exceeds ninety days and `outcome` is empty. Cases opened
within the last ninety days with an empty outcome are silently
accepted; the scorer treats them as `still-pending`.

## What the score is not

- It is not a quality score for the pattern itself. A pattern with a
  low transfer index may still be the right pattern; the cases may
  have been bad fits.
- It is not a forecast. Past transfers do not predict future
  transfers, especially in a corpus this small.
- It is not normalized across quarters. Comparing `2026-Q2` to
  `2026-Q3` is fine; comparing to a quarter with five times the case
  count is not.

## Calibration

The 0.5 weight on `transferred-with-friction` is a default, not a fit.
Calibration is a queued task:

1. Sample ten past cases across the seed patterns.
2. Have a human score each on a 0-to-1 transfer quality scale.
3. Fit the friction weight so the resulting `transfer_index`
   minimizes squared error against the human scores.
4. Record the fitted weight and the calibration data in
   `DEC-PPL-002-friction-weight-calibration.md`.

Until that DEC lands, the weight is a stated assumption, not a result.
Every ledger row records the weight in use so future re-scoring
against the calibrated weight is mechanical.

## Reproducibility

Every scoring run writes a ledger row containing the input counts, the
weights used, the per-pattern scores, and the current date. Re-running
`score` on the same quarter with the same corpus must produce the same
row, byte-for-byte, with the exception of the `generated_at`
timestamp. The tests under `tests/test_score.py` lock this in.

## What revisits this

This methodology is not load-bearing forever. The list below names
each event that should cause a reader to come back here and update
this doc plus the matching code, so a stale weight or rule does not
silently drift away from the implementation.

- **Calibration DEC lands.** When
  `DEC-PPL-002-friction-weight-calibration.md` is checked in, update
  the friction weight default in `score.py`, update the weights table
  at the top of this doc, and update the Calibration section so it
  points at the DEC instead of describing queued work.
- **Outcome enum changes.** If a new outcome value is added (for
  example, a `transferred-and-extended` value to capture cases where
  the pattern was generalized in flight), update the enum table, the
  schema under `schemas/case.schema.json`, the scorer in `score.py`,
  and the validator.
- **Ninety-day rule shifts.** If the ninety-day window proves too
  short or too long against the next year of cases, update the rule
  in `validator.py`, record the change in a DEC, and update the
  "Ninety-day outcome rule" section above.
- **Quarterly scoring run.** On every quarterly run, re-read this doc
  before publishing the retro. If anything in the methodology diverges
  from what the new ledger row records, the doc is stale — fix the
  doc, not the row.
- **Corpus crosses fifteen patterns.** At that threshold the retro's
  "rising did-not-transfer" signal becomes meaningful. Add a section
  to this doc on how that trend signal is computed and revisit the
  "What the score is not" caveats.
- **Schema migration.** Any change to `schemas/pattern.schema.json`,
  `schemas/case.schema.json`, or `schemas/retro.schema.json` should
  trigger a pass over this doc to confirm the Inputs section still
  describes what the loader actually parses.
