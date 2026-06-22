# System map — procurement-pattern-library

How the pieces fit together. The map is intentionally small: this
repo is a typed corpus and a thin CLI, not an application.

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
|  (schema +  |   | (transfer |   | (markdown printer   |
|  outcome    |   |  index +  |   |  over scorer        |
|  rule)      |   |  ledger   |   |  output)            |
|             |   |  writer)  |   |                     |
+------+------+   +-----+-----+   +----------+----------+
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

1. The loader walks `patterns/`. For each `<id>.md` it parses the
   YAML front-matter and the body, then walks the sibling
   `applications/` directory and parses every case file the same
   way.
2. The validator takes the loader output and checks each parsed
   front-matter against the schema in `schemas/`. It also applies
   the ninety-day outcome rule: any case with `opened_at` older
   than ninety days from today and an empty `outcome` is an error.
3. The scorer takes the loader output, filters cases to the named
   quarter, and computes a per-pattern transfer index. The output
   is a list of `PatternScore` records and a summary, written to
   `ledger/runs/<run-id>.md` as YAML front-matter plus a short
   human-readable body.
4. The retro renderer reads a ledger run row, sorts patterns by
   transfer index, and prints a Markdown table to stdout. The
   v0.1 renderer does not persist; a later spec wires it to write
   `retros/<quarter>.md`.

## File responsibilities

| Path | Role |
|---|---|
| `procurement_pattern_library/cli.py` | Argparse entry point |
| `procurement_pattern_library/__main__.py` | `python -m` shim |
| `procurement_pattern_library/loader.py` | Walk + parse YAML front-matter |
| `procurement_pattern_library/validator.py` | Schema + outcome rule |
| `procurement_pattern_library/score.py` | Transfer index + ledger writer |
| `procurement_pattern_library/retro.py` | Markdown table printer |
| `schemas/*.json` | Pattern, case, retro front-matter shapes |
| `patterns/*.md` | One pattern per file |
| `patterns/<id>/applications/*.md` | One case per file |
| `decisions/DEC-PPL-*.md` | Architectural decision records |
| `ledger/runs/*.md` | One row per scoring run |
| `tests/test_*.py` | Unit + smoke coverage |
| `scripts/validate_*.py` | Standalone gates re-using the validator |

## What is not in the map

- No web server, no daemon, no scheduler. The CLI is invoked by a
  human or by the factory.
- No database. The corpus is the filesystem.
- No external API calls. Validation is local-only; URIs are not
  de-referenced.
