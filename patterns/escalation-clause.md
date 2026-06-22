---
id: escalation-clause
name: Escalation clause for asymmetric exceptions
canonical_statement: Pre-negotiate the path that exceptions take so the exceptional case does not become a bilateral re-negotiation under time pressure.
domains: [procurement, mechanism-design, ai-build]
created_at: 2026-06-19
applications_dir: applications/
---

# Escalation clause for asymmetric exceptions

A contract or process step that names, in advance, what
happens when an input falls outside the normal envelope. The
clause states the trigger condition, the named owner of the
escalation, and the time bound on the decision. The point is
that the exception path is decided when both sides have time
to think, not when one side is under deadline pressure.

## When it applies

- A small fraction of cases will need a non-standard decision,
  and the decision has time pressure when it arrives.
- The cost of the wrong decision under pressure is much higher
  than the cost of pre-negotiating the path.
- The escalation owner is named and reachable; "the team" is
  not a valid owner.

## When it does not apply

- All cases are routine. Escalation overhead pays for nothing.
- The exception path is so case-specific that no pre-
  negotiation is meaningful.
- No real owner exists; the clause becomes a fiction that
  papers over the lack of accountability.

## Anti-patterns

- An escalation clause that names a team mailbox rather than a
  person. Under pressure, no one owns it.
- An unbounded time clause ("escalation will be reviewed
  promptly"). Promptly is not a number.
- A clause that the named owner has never seen.

## Cross-domain reading

In an AI build with a human review queue, the same shape is a
reviewer-escalation path: cases that score above or below a
threshold are routed to a named reviewer with a stated SLA. The
mechanism-design lesson is that the queue's exception path
should be designed at the same time as the routing rule, not
discovered when the first exception arrives.
