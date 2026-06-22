"""Confirm every JSON schema file parses as valid JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"


def main() -> int:
    errors: list[str] = []
    for schema_path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        try:
            data = json.loads(schema_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{schema_path}: invalid JSON: {e}")
            continue
        if not isinstance(data, dict):
            errors.append(f"{schema_path}: top level must be an object")
            continue
        for required in ("$schema", "title", "type"):
            if required not in data:
                errors.append(f"{schema_path}: missing top-level {required!r}")
    for e in errors:
        print(e, file=sys.stderr)
    print(
        f"checked {sum(1 for _ in SCHEMAS_DIR.glob('*.schema.json'))} schema file(s); "
        f"{len(errors)} error(s)."
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
