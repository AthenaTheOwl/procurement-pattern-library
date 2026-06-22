---
id: eval-budget-reservation
pattern_id: capacity-reservation
domain: ai-build
upstream_artifact: repo://supplier-risk-rag-agent/decisions/DEC-SRRA-022-eval-budget.md
opened_at: 2026-05-10
outcome: transferred-cleanly
---

# Eval-budget reservation in supplier-risk-rag-agent

Supplier-risk-rag-agent runs a large LLM-eval pass before each
release. Two prior releases bid for token capacity during the
release window and paid a measurable spot premium.

The pattern was applied to reserve the eval token budget two
weeks ahead of the release window at the published off-window
rate. The reservation was sized to ninety percent of the prior
release's actual eval consumption, which kept the unused share
under three percent of the budget. The transfer was clean:
the predicted off-window rate held, the reservation covered
the run, and the spot premium was avoided. The case is the
cleanest cross-application of the pattern logged so far.
