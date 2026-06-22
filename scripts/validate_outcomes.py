"""Standalone gate: enforce the ninety-day outcome rule only."""

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
    outcome_errors = [i for i in result.errors if "empty outcome" in i.message]
    for issue in outcome_errors:
        rel = issue.path
        try:
            rel = issue.path.relative_to(REPO_ROOT)
        except ValueError:
            pass
        print(f"ERROR   {rel}: {issue.message}")
    print(
        f"checked {len(corpus.cases)} case(s); "
        f"{len(outcome_errors)} outcome-rule violation(s)."
    )
    return 0 if not outcome_errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
