# Requirements — 0001 Foundation

Numbered requirements for the v0 scaffold of procurement-pattern-
library. The R-PPL-* prefix is the brand tag and appears in every
downstream spec, decision, and gate.

## Patterns

- **R-PPL-001** Each pattern lives at `patterns/<pattern-id>.md`
  with a YAML front-matter block matching the pattern schema. The
  schema is under `schemas/pattern.schema.json`.
- **R-PPL-002** A pattern front-matter has `id`, `name`,
  `canonical_statement`, `domains[]`, `created_at`,
  `applications_dir`.
- **R-PPL-003** `domains[]` is a non-empty array drawn from the
  enum `procurement`, `supply-chain`, `mechanism-design`,
  `ai-build`. A pattern must declare at least one domain.

## Application cases

- **R-PPL-004** Application cases live at
  `patterns/<pattern-id>/applications/<case-id>.md` with their own
  YAML front-matter block matching `schemas/case.schema.json`.
- **R-PPL-005** A case front-matter has `id`, `pattern_id`,
  `domain` (single value from the same enum), `upstream_artifact`,
  `opened_at`, `outcome`.
- **R-PPL-006** `upstream_artifact` is a URI-shaped string pointing
  at a DEC, brief, factory run, or other typed artifact in the
  portfolio.
- **R-PPL-007** `outcome` is optional at case creation. A case
  becomes invalid if it is older than ninety days and the outcome
  is still empty. `outcome` is an enum: `transferred-cleanly`,
  `transferred-with-friction`, `did-not-transfer`, `still-pending`.

## Retros

- **R-PPL-008** A quarterly retro lives at `retros/<quarter>.md`
  and is generated from the patterns plus their cases. It names
  the top patterns by transfer count, the patterns with rising
  did-not-transfer counts, and the patterns with no cases yet.

## Seed corpus

- **R-PPL-009** v0 ships at least three pattern files seeded from
  the existing portfolio decisions ledger. Each seed pattern has
  at least two application cases.

## Governance

- **R-PPL-010** Architectural choices are recorded in
  `decisions/DEC-PPL-NNN-<slug>.md`. The first decision
  (DEC-PPL-001) justifies the four-domain enum closure and the
  ninety-day outcome rule.
