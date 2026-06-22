---
id: reviewer-escalation-ai-field-brief
pattern_id: escalation-clause
domain: ai-build
upstream_artifact: repo://ai-field-brief/decisions/DEC-AFB-017-reviewer-escalation.md
opened_at: 2026-05-22
outcome: still-pending
---

# Reviewer escalation in the ai-field-brief review queue

The ai-field-brief queue routes generated briefs through a
human reviewer when the model's self-rated confidence falls
below a threshold. The escalation-clause pattern was applied
to design the path before the queue went live: the named
escalation owner is a specific reviewer (not a rotation), the
SLA is one business day, and the trigger is a confidence score
below 0.6 on any required-field check.

The case is still pending. The queue went live inside the
ninety-day window, but not enough briefs have triggered the
escalation path to know whether the SLA holds under volume. A
re-score in the next quarterly retro will move this to one of
the three terminal outcomes.
