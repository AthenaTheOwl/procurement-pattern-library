# AGENTS.md — procurement-pattern-library

Operating contract for AI agents working in this repo. Conventions
match the AthenaTheOwl portfolio so an agent already trained on
procurement-negotiation-lab or supplier-risk-rag-agent recognizes
the shape.

## What this repo is

A typed library of patterns plus their cross-applications. Each
pattern file is a small unit of knowledge with a front-matter block
and a typed `applications/` subdirectory. The library is checked-in
Markdown; the validator confirms typing; the quarterly retro is a
report renderer.

This is a personal knowledge primitive, not a public docs site.

## Roles you may see in tasks

| Role | What they do |
|---|---|
| `pattern-author` | Drafts a new pattern file with the required front-matter |
| `case-binder` | Adds an application case under a pattern's applications dir |
| `outcome-recorder` | Fills the outcome field on a case ninety days later |
| `retro-writer` | Composes the quarterly retro across patterns |
| `validator` | Confirms every pattern and case is well-typed |

These roles exist in the spec ledger; not all are implemented in v0.

## Voice constraints

- No marketing words. The banned set will live in
  `scripts/voice_lint.py::BANNED_FAIL` once the gate lands.
- No antithetical reversals as a structural device.
- A pattern's canonical statement is one sentence, plain assertion.
- Cross-applications cite the upstream artifact (a DEC, a brief, a
  factory run) by URI.

## Gates (will land in spec 0002)

Planned local gates before pushing:

- `pytest`
- `voice_lint.py` on `patterns/**/*.md` and `retros/*.md`
- `spec_check.py` against `specs/`
- `validate_patterns.py` — every pattern file is well-typed; every
  application case parses and points at a real upstream artifact
- `validate_outcomes.py` — every case older than ninety days has a
  filled outcome field

## Out of scope

- A web docs site. Markdown under `patterns/` is the artifact.
- LLM-generated pattern files. Patterns are hand-authored; the
  retro renderer is mechanical.
- Patterns outside the procurement / supply-chain / mechanism-design
  axis. v0 is scoped to the user's day-job and AI-build leverage.
- Cross-author contribution flow. v0 is single-author.
