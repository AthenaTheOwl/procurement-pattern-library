---
id: model-routing-fallback
pattern_id: dual-source
domain: ai-build
upstream_artifact: repo://athena-site/decisions/DEC-AS-042-model-fallback.md
opened_at: 2026-05-03
outcome: transferred-with-friction
---

# Model routing fallback in the Athena site

The AI-build mirror of the bauxite case. The Athena site had a
single primary model behind a critical generation endpoint. A
regional outage at the model provider took the endpoint down
for ninety minutes.

The fix instanced the pattern: a secondary model with the same
request shape, kept warm by routing five percent of traffic.
The transfer was not clean. The friction came from prompt
divergence: the primary and secondary models accepted the same
prompt but produced systematically different output shapes,
which forced a downstream normalization layer. The pattern
applied — the redundancy paid off in the next regional outage
two months later — but the integration cost was higher than
the bauxite case predicted, because the procurement primitive
assumed fungibility that did not fully hold across models.

The lesson recorded back in the pattern body is that
fungibility is a stronger assumption in physical commodities
than in language models, and the dual-source pattern should be
applied with a normalization layer planned from day one in the
ai-build domain.
