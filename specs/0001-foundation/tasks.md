# Tasks — 0001 Foundation

Checkbox tasks ordered for the first two to three PRs after the
scaffold.

## PR 1 — Schemas and three seed patterns

- [ ] Write `schemas/pattern.schema.json` per R-PPL-001
- [ ] Write `schemas/case.schema.json` per R-PPL-004
- [ ] Write `schemas/retro.schema.json`
- [ ] Author `patterns/dual-source.md` with two application cases
      under `patterns/dual-source/applications/`
- [ ] Author `patterns/escalation-clause.md` with two cases
- [ ] Author `patterns/capacity-reservation.md` with two cases
- [ ] Add `decisions/DEC-PPL-001-domain-closure-and-outcome-rule.md`
- [ ] Add `scripts/validate_schemas.py` skeleton
- [ ] Add `scripts/validate_patterns.py` skeleton

## PR 2 — Outcome validator and voice gate

- [ ] Add `scripts/validate_outcomes.py` enforcing the ninety-day
      outcome rule
- [ ] Add `scripts/voice_lint.py` skeleton
- [ ] Write a fixture case with an outcome older than ninety days
      and confirm the validator flags it; fix the case
- [ ] Wire CLI entry: `python -m procurement_pattern_library
      validate`

## PR 3 — Retro renderer and DEC ledger

- [ ] Implement `src/procurement_pattern_library/retro.py`
- [ ] Add `templates/retro.md.j2`
- [ ] Render the first retro at `retros/2026-Q2.md` from the seed
      corpus
- [ ] Add `scripts/validate_decisions.py` skeleton
- [ ] Document the retro mechanic in DEC-PPL-002
- [ ] Update README install + run section once `validate` and
      `retro` both work
