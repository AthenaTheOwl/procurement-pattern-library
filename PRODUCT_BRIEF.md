# Product brief — procurement-pattern-library

This file is the canonical product brief and lives at the repo root so
the factory contract gate finds it without walking subdirectories. The
prose version under `docs/product-brief.md` is the same content kept
for human readers who browse the docs directory; if the two ever
diverge, this root file wins.

## What it is

A typed, hand-authored library of patterns from the procurement,
supply-chain, and mechanism-design world, each paired with a growing
list of application cases drawn from AI-build work. The library is
checked-in Markdown. A small Python CLI keeps the typing honest, scores
the corpus into a per-pattern transfer index every quarter, and writes
the score out to two ledger surfaces — a human-readable Markdown row
under `ledger/runs/` and a machine-readable JSONL row under
`data/ledger/`.

## Who it is for

The primary reader is Vignesh, using the library as a personal
knowledge primitive across two day-jobs: procurement / mechanism
design on one side, AI systems work on the other. The library exists
to make the transfer between the two explicit instead of implicit.

A secondary reader is any outside collaborator who wants to see how
patterns move between domains. The library is not a public docs site;
it is a personal corpus published in the open.

A tertiary, eventual reader is a downstream agent that can ground on
the typed corpus when reasoning about a new mechanism-design problem.
The JSONL ledger under `data/ledger/` exists for that agent.

## What problem it solves

The portfolio's existing decisions ledger has cross-domain transfers
buried inside individual DECs. Reading one DEC does not tell a reader
which broader pattern it instances. A pattern lookup is structurally a
join across the ledger, and that join was implicit. This repo lifts
the join into a typed object so it can be queried and scored.

## What "v0.1 done" looks like

- Three seed patterns checked in, each with two typed application
  cases.
- Schemas for pattern, case, and retro front-matter.
- A Python CLI with three subcommands: `validate`, `score`, `retro`.
- One checked-in scoring run as a Markdown row under
  `ledger/runs/` and as a JSONL row under `data/ledger/`,
  representing the state of the library as of the v0.1 PR.
- Tests covering loader, validator, scorer, ledger writer, and
  report renderer.

## What "v1 done" would look like

- Fifteen patterns minimum, so the rising did-not-transfer signal in
  the retro becomes meaningful.
- The retro / report renderer writes a Markdown report per quarter
  and the report is checked in under `retros/`.
- The voice-lint gate fails on banned marketing language.
- The scoring methodology is calibrated against a hand-scored panel
  and the weight is recorded in `DEC-PPL-002`.

## What is explicitly out of scope

- A web docs site.
- LLM-generated pattern files. Patterns are hand-authored.
- Cross-author contribution flow.
- Patterns outside the procurement / supply-chain / mechanism-design
  / ai-build axis.
- Auto-extraction of patterns from the decisions ledger. That is a
  future spec.
