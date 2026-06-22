---
id: capacity-reservation
name: Capacity reservation against contention windows
canonical_statement: When a shared resource is contention-priced during a known window, pre-reserve the capacity at the lower off-window price rather than bidding into the peak.
domains: [procurement, supply-chain, mechanism-design, ai-build]
created_at: 2026-06-19
applications_dir: applications/
---

# Capacity reservation against contention windows

A primitive from capacity-constrained markets. Some shared
resource — warehouse space, manufacturing time, model tokens —
is contention-priced during a known window and underutilized
outside it. Pre-reserving capacity at the off-window price
beats bidding into the peak, provided the reservation cost is
less than the expected peak premium times the probability of
needing the capacity.

## When it applies

- A known window has predictable contention and predictable
  pricing.
- The reservation can be sized close to actual need so the
  paid-for-but-unused capacity is bounded.
- The off-window price is materially below the peak price.

## When it does not apply

- The window is unpredictable. Pre-reservation is a guess.
- The reservation cost is non-refundable and the demand is
  highly variable; the expected cost of over-reservation
  exceeds the expected savings.
- Spot capacity is reliably available; the contention premium
  is rumored, not real.

## Anti-patterns

- Reserving capacity to the upper end of a forecast and
  treating the unused share as sunk; over time, the
  reservation grows to fit the budget rather than the need.
- Reserving with a counterparty whose own capacity is not
  contracted; the reservation is a promise, not a guarantee.
- Reserving capacity that the buyer cannot itself absorb
  (warehouse slots a buyer cannot fill, tokens a buyer cannot
  spend before they expire).

## Cross-domain reading

In an AI build, the same shape is an eval-budget reservation:
LLM-eval token capacity is contention-priced during a release
window. Reserving a token budget against the upcoming release
at the off-window rate is cheaper than bidding into spot at
the release. The mechanism-design lesson — size the
reservation close to the actual need — applies identically.
