---
id: dual-source
name: Dual-source the critical path
canonical_statement: When one node failing kills the whole flow, run two suppliers in parallel and pay the redundancy cost.
domains: [procurement, supply-chain, ai-build]
created_at: 2026-06-19
applications_dir: applications/
---

# Dual-source the critical path

A canonical procurement primitive. If a single supplier of a
critical input can take the whole flow offline by failing,
defaulting, or being acquired, the cost of running a second
supplier in parallel is paid as insurance. The redundancy cost
is real and is weighed against the cost of a single-source
outage times the probability of one.

## When it applies

- A single failure in the input kills the dependent output. No
  graceful degradation is available.
- The supplier is meaningfully fungible: a second source can be
  brought online without re-engineering the dependent process.
- The redundancy cost is bounded and predictable.

## When it does not apply

- The input is non-fungible (a single named expert, a single
  named regulator). Dual-sourcing is a category error.
- The dependent process tolerates degraded output. A retry or a
  fallback to a cached value is cheaper than a second supplier.
- The redundancy cost is unbounded (every additional source
  triples the integration cost).

## Anti-patterns

- "Dual-source" that is actually a primary plus a stale, never-
  exercised secondary. The secondary fails on first use because
  it was never load-tested.
- Splitting volume 50/50 between two suppliers when the failure
  mode is correlated (both depend on the same upstream).
- Negotiating away the redundancy after a quiet quarter, then
  losing the supply when the inevitable failure arrives.

## Cross-domain reading

In an AI build, the same shape appears as model routing
fallback: a primary model with a warm secondary that handles
the same request shape, exercised on a fraction of traffic to
keep the failover path honest. The integration cost is real;
the correlated-failure trap (both models share an upstream like
a single cloud region) is the same trap.
