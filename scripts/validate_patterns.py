"""Standalone gate: re-runs the in-process validator against the repo."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from procurement_pattern_library.loader import load_corpus  # noqa: E402
from procurement_pattern_library.validator import validate  # noqa: E402


def main() -> int:
    corpus = load_corpus(REPO_ROOT)
    result = validate(corpus, today=date.today())
    for issue in result.issues:
        rel = issue.path
        try:
            rel = issue.path.relative_to(REPO_ROOT)
        except ValueError:
            pass
        print(f"{issue.severity.upper():7} {rel}: {issue.message}")
    print(
        f"validated {len(corpus.patterns)} pattern(s), "
        f"{len(corpus.cases)} case(s); "
        f"{len(result.errors)} error(s), {len(result.warnings)} warning(s)."
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
