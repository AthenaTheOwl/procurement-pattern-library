"""Standalone gate: enforce the ninety-day outcome rule only."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from procurement_pattern_library.loader import load_corpus  # noqa: E402
from procurement_pattern_library.validator import OUTCOME_RULE, validate  # noqa: E402


def main(root: Path = REPO_ROOT, today: date | None = None) -> int:
    corpus = load_corpus(root)
    result = validate(corpus, today=today or date.today())
    outcome_errors = [i for i in result.errors if OUTCOME_RULE in i.message]
    for issue in outcome_errors:
        rel = issue.path
        try:
            rel = issue.path.relative_to(root)
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
