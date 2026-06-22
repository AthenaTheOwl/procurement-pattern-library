# System map — procurement-pattern-library

This file is the canonical system map and lives at the repo root so the
factory contract gate finds it without walking subdirectories. The
prose version under `docs/system-map.md` is the same content kept for
human readers; if the two ever diverge, this root file wins.

The repo is intentionally small: a typed corpus and a thin Python CLI,
not an application.

## Layers

```
+---------------------------------------------------------------+
|                       CLI (entry point)                       |
|         python -m procurement_pattern_library <sub>           |
|                                                               |
|  validate    score    retro                                   |
+--------+-------------+-------------+--------------------------+
         |             |             |
         v             v             v
+--------+----+   +----+------+   +--+-------------------+
|  validator  |   |  scorer   |   |   retro renderer    |
|  (schema +  |   | (transfer |   |   /  report writer  |
|  outcome    |   |  index)   |   |                     |
|  rule)      |   |           |   |                     |
+------+------+   +-----+-----+   +----------+----------+
       |                |                    |
       |                v                    |
       |          +-----+--------+           |
       |          | ledger.py    |           |
       |          | (JSONL +     |           |
       |          |  Markdown    |           |
       |          |  row writer) |           |
       |          +-----+--------+           |
       |                |                    |
       +--------+-------+--------------------+
                |
                v
       +--------+--------+
       |     loader      |
       | (yaml + body    |
       |  splitter, walk |
       |  patterns/,     |
       |  decisions/)    |
       +--------+--------+
                |
                v
       +--------+--------+
       |  typed corpus   |
       |                 |
       | patterns/*.md   |
       | patterns/*/     |
       |   applications  |
       |   /*.md         |
       | decisions/*.md  |
       | schemas/*.json  |
       +-----------------+
```

## Data flow

1. The loader walks `patterns/`. For each `<id>.md` it parses the YAML
   front-matter and the body, then walks the sibling `applications/`
   directory and parses every case file the same way.
2. The validator takes the loader output and checks each parsed
   front-matter against the schema in `schemas/`. It also applies the
   ninety-day outcome rule: any case with `opened_at` older than
   ninety days from today and an empty `outcome` is an error.
3. The scorer takes the loader output, filters cases to the named
   quarter, and computes a per-pattern transfer index. The output is a
   `RunResult` dataclass.
4. The ledger writer (`ledger.py`) persists a `RunResult` to two
   surfaces — a Markdown row under `ledger/runs/<run-id>.md` for human
   readers and a JSON row under `data/ledger/<run-id>.jsonl` for the
   downstream agent.
5. The retro / report renderer (`retro.py`, `report.py`) reads a
   ledger row and prints / writes a Markdown table.

## File responsibilities

| Path | Role |
|---|---|
| `procurement_pattern_library/cli.py` | Argparse entry point |
| `procurement_pattern_library/__main__.py` | `python -m` shim |
| `procurement_pattern_library/loader.py` | Walk + parse YAML front-matter |
| `procurement_pattern_library/validator.py` | Schema + outcome rule |
| `procurement_pattern_library/score.py` | Transfer-index computation |
| `procurement_pattern_library/ledger.py` | JSONL + Markdown ledger writer/reader |
| `procurement_pattern_library/report.py` | Markdown report writer |
| `procurement_pattern_library/retro.py` | Markdown table printer (stdout) |
| `schemas/*.json` | Pattern, case, retro front-matter shapes |
| `patterns/*.md` | One pattern per file |
| `patterns/<id>/applications/*.md` | One case per file |
| `decisions/DEC-PPL-*.md` | Architectural decision records |
| `ledger/runs/*.md` | One Markdown row per scoring run (human-readable) |
| `data/ledger/*.jsonl` | One JSON row per scoring run (machine-readable) |
| `tests/test_*.py` | Unit + smoke coverage |
| `scripts/validate_*.py` | Standalone gates re-using the validator |

## What is not in the map

- No web server, no daemon, no scheduler. The CLI is invoked by a
  human or by the factory.
- No database. The corpus is the filesystem.
- No external API calls. Validation is local-only; URIs are not
  de-referenced.
