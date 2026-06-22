---
id: DEC-PPL-001
title: Close the domain enum at four members; fix the outcome window at ninety days
status: accepted
date: 2026-06-22
authors: [Vignesh]
supersedes: []
superseded_by: []
---

# DEC-PPL-001 — Domain closure and outcome rule

## Context

The pattern library needs two things settled before any pattern
file is written, because both shape the schema and the gate:

1. The list of allowed values for the `domains[]` field on a
   pattern and the `domain` field on a case.
2. The time window after which an empty `outcome` on a case is
   a validator error.

Both choices look like they could be deferred, but in practice
the schemas need to commit to a closed enum and a numeric
threshold so the validator can be mechanical. Deferring the
choices means deferring the validator, which means the corpus
can drift before there is a gate.

## Decision

The `domains[]` enum is closed at four values:

- `procurement`
- `supply-chain`
- `mechanism-design`
- `ai-build`

The outcome window is ninety days from `opened_at`. A case
older than ninety days with an empty `outcome` is a validator
error.

## Domains considered and deferred

| Domain | Why deferred |
|---|---|
| `legal-contracts` | Patterns are about deal shape; legal review of a clause is downstream and ends up cross-applied as a procurement or mechanism-design pattern anyway. |
| `sales-comp` | The portfolio does not include sales-comp design work; adding a domain with zero cases inflates the enum without earning its keep. |
| `hiring` | Patterns from the hiring process (signal vs. noise in interviews, escalation paths for borderline decisions) are real cross-domain candidates but are scoped to a different repo. |
| `research-ops` | Considered as a separate label for research processes; rejected because the ones that transfer cleanly fit under `mechanism-design`. |

The closure can be revisited in a follow-up DEC. Re-opening
the enum is a schema change, so the bar is intentionally high.

## Why ninety days

The window is a calibration of two costs.

- Too short, and the validator fails on cases whose outcome is
  genuinely not yet observable — most ai-build cases need at
  least a release cycle to land.
- Too long, and the library accumulates ambiguous rows that
  the scorer cannot use, draining the retro of signal.

Ninety days lines up with a quarterly cadence. The first
scoring run at end-of-quarter sees every case from the prior
quarter as scored, not pending. Anything still pending after
ninety days is genuinely stuck and worth surfacing.

The window can be revisited per-domain in a follow-up DEC if
one domain consistently needs more time.

## Consequences

- The schemas under `schemas/` encode the four-value enum
  directly. Adding a domain is a schema bump and a coordinated
  edit across pattern files.
- The validator under `src/procurement_pattern_library/
  validator.py` treats the ninety-day rule as an error, not a
  warning.
- The retro's "still-pending" bucket only contains cases under
  ninety days old. A pending case older than that is an
  invariant violation, not a retro entry.
