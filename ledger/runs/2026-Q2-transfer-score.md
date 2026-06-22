---
run_id: 2026-Q2-transfer-score
generated_at: '2026-06-22'
quarter: 2026-Q2
friction_weight: 0.5
inputs:
  patterns: 3
  cases: 5
scores:
- pattern_id: capacity-reservation
  case_count: 2
  transfer_index: 0.75
  strict_index: 0.5
  outcomes:
    transferred-cleanly: 1
    transferred-with-friction: 1
- pattern_id: dual-source
  case_count: 2
  transfer_index: 0.75
  strict_index: 0.5
  outcomes:
    transferred-cleanly: 1
    transferred-with-friction: 1
- pattern_id: escalation-clause
  case_count: 1
  transfer_index: null
  strict_index: null
  outcomes:
    still-pending: 1
---

# Scoring run — 2026-Q2

Per-pattern transfer index for 2026-Q2, computed from 5 case(s)
across 3 pattern(s) in the corpus. Friction weight in use: 0.5.

| Pattern | Cases | Transfer index | Strict index |
|---|---:|---:|---:|
| capacity-reservation | 2 | 0.75 | 0.50 |
| dual-source | 2 | 0.75 | 0.50 |
| escalation-clause | 1 | — | — |

## Reading

Two patterns landed at the same transfer index (0.75) and the
same strict index (0.5) — one clean transfer and one with
friction each, for `capacity-reservation` and `dual-source`. The
gap between transfer index and strict index for both is the
friction weight in action: half-credit on the friction case
pulls the strict score down to 0.5 while the friction-adjusted
score sits at 0.75.

`escalation-clause` has one case in the quarter, still pending.
No signal yet; the case stays on the watch list for the next
quarterly run.

`escalation-clause/long-tail-vendor-2024` was opened in
2026-Q1 (2026-03-15) and so does not appear in the 2026-Q2
input set. It will appear in the rolling annual view a later
spec will add.

## Calibration notes

Friction weight is the default 0.5. No calibration data was
folded in; that work is queued under DEC-PPL-002. The strict
index column lets a future reader re-derive the score with a
different weight without re-running the corpus.
