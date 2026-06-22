# Product brief — procurement-pattern-library

A short statement of what this repo is for, who it is for, and what
"done" looks like at each horizon. The brief is the contract a
contributor reads first; it overrides anything in this repo's other
docs that contradicts it.

## What it is

A typed, hand-authored library of patterns from the procurement,
supply-chain, and mechanism-design world, each paired with a
growing list of application cases drawn from AI-build work. The
library is checked-in Markdown. A small Python CLI keeps the
typing honest and rolls the library up into a quarterly score.

## Who it is for

The primary reader is Vignesh, using the library as a personal
knowledge primitive across two day-jobs: procurement / mechanism
design on one side, AI systems work on the other. The library
exists to make the transfer between the two explicit instead of
implicit.

A secondary reader is any outside collaborator who wants to see
how patterns move between domains. The library is not a public
docs site; it is a personal corpus published in the open.

A tertiary, eventual reader is a downstream agent that can ground
on the typed corpus when reasoning about a new mechanism-design
problem.

## What problem it solves

The portfolio's existing decisions ledger has cross-domain
transfers buried inside individual DECs. Reading one DEC does not
tell a reader which broader pattern it instances. A pattern lookup
is structurally a join across the ledger, and that join was
implicit. This repo lifts the join into a typed object so it can
be queried and scored.

## What "v0.1 done" looks like

- Three seed patterns checked in, each with two typed application
  cases.
- Schemas for pattern, case, and retro front-matter.
- A Python CLI with three subcommands: validate, score, retro.
- One checked-in scoring run under `ledger/runs/` representing
  the state of the library as of the v0.1 PR.
- Tests covering loader, validator, and scorer.

## What "v1 done" would look like

- Fifteen patterns minimum, so the rising did-not-transfer
  signal in the retro becomes meaningful.
- The retro renderer writes a Markdown report per quarter and
  the report is checked in.
- The voice-lint gate fails on banned marketing language.
- The scoring methodology is calibrated against a hand-scored
  panel and the weight is recorded in a DEC.

## What is explicitly out of scope

- A web docs site.
- LLM-generated pattern files. Patterns are hand-authored.
- Cross-author contribution flow.
- Patterns outside the procurement / supply-chain /
  mechanism-design / ai-build axis.
- Auto-extraction of patterns from the decisions ledger. That is
  a future spec.
