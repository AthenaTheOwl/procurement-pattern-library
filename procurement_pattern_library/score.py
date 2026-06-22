"""Per-pattern transfer-index scoring and ledger-row writer."""

from __future__ import annotations

import io
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable

import yaml

from .loader import Case, Corpus

QUARTER_MONTHS = {1: (1, 3), 2: (4, 6), 3: (7, 9), 4: (10, 12)}


class ScoreError(ValueError):
    """Bad input to the scorer."""


@dataclass(frozen=True)
class ScoreWeights:
    friction_weight: float = 0.5


@dataclass(frozen=True)
class PatternScore:
    pattern_id: str
    case_count: int
    transfer_index: float | None
    strict_index: float | None
    outcomes: dict[str, int]


@dataclass(frozen=True)
class RunResult:
    run_id: str
    generated_at: date
    quarter: str
    weights: ScoreWeights
    inputs: dict[str, int]
    scores: list[PatternScore]


def parse_quarter(q: str) -> tuple[date, date]:
    """Return (start_date, end_date_inclusive) for a YYYY-Qn string."""
    try:
        year_s, qpart = q.split("-Q")
        year = int(year_s)
        qnum = int(qpart)
    except ValueError as e:
        raise ScoreError(f"invalid quarter format {q!r}; expected YYYY-Qn") from e
    if qnum not in QUARTER_MONTHS:
        raise ScoreError(f"quarter number must be 1..4, got {qnum}")
    start_month, end_month = QUARTER_MONTHS[qnum]
    start = date(year, start_month, 1)
    if end_month == 12:
        end = date(year, 12, 31)
    else:
        # last day of end_month
        next_first = date(year, end_month + 1, 1)
        end = date.fromordinal(next_first.toordinal() - 1)
    return start, end


def _opened_in_quarter(c: Case, start: date, end: date) -> bool:
    raw = c.front_matter.get("opened_at")
    if isinstance(raw, date):
        d = raw
    elif isinstance(raw, str):
        try:
            d = date.fromisoformat(raw)
        except ValueError:
            return False
    else:
        return False
    return start <= d <= end


def _score_one(
    pattern_id: str,
    cases: Iterable[Case],
    weights: ScoreWeights,
) -> PatternScore:
    outcomes = Counter()
    for c in cases:
        raw = c.front_matter.get("outcome")
        if raw is None or raw == "":
            outcomes["still-pending"] += 1
        else:
            outcomes[str(raw)] += 1

    scored = (
        outcomes["transferred-cleanly"]
        + outcomes["transferred-with-friction"]
        + outcomes["did-not-transfer"]
    )
    if scored == 0:
        transfer_index = None
        strict_index = None
    else:
        transfer_index = round(
            (
                outcomes["transferred-cleanly"] * 1.0
                + outcomes["transferred-with-friction"] * weights.friction_weight
            )
            / scored,
            4,
        )
        strict_index = round(outcomes["transferred-cleanly"] / scored, 4)

    return PatternScore(
        pattern_id=pattern_id,
        case_count=sum(outcomes.values()),
        transfer_index=transfer_index,
        strict_index=strict_index,
        outcomes={k: outcomes[k] for k in sorted(outcomes) if outcomes[k] > 0},
    )


def score_quarter(
    corpus: Corpus,
    quarter: str,
    weights: ScoreWeights | None = None,
    today: date | None = None,
) -> RunResult:
    weights = weights or ScoreWeights()
    today = today or date.today()
    start, end = parse_quarter(quarter)

    cases_in_q = [c for c in corpus.cases if _opened_in_quarter(c, start, end)]
    patterns_in_q: dict[str, list[Case]] = {}
    for c in cases_in_q:
        pid = c.pattern_id
        patterns_in_q.setdefault(pid, []).append(c)

    # include every pattern in the corpus, even those with no cases this quarter
    for p in corpus.patterns:
        patterns_in_q.setdefault(p.id, [])

    scores = [
        _score_one(pid, patterns_in_q[pid], weights)
        for pid in sorted(patterns_in_q)
    ]
    # sort: highest transfer_index first, then highest case_count, then id
    scores.sort(
        key=lambda s: (
            -(s.transfer_index if s.transfer_index is not None else -1.0),
            -s.case_count,
            s.pattern_id,
        )
    )

    return RunResult(
        run_id=f"{quarter}-transfer-score",
        generated_at=today,
        quarter=quarter,
        weights=weights,
        inputs={"patterns": len(corpus.patterns), "cases": len(cases_in_q)},
        scores=scores,
    )


def _result_to_frontmatter(result: RunResult) -> dict:
    return {
        "run_id": result.run_id,
        "generated_at": result.generated_at.isoformat(),
        "quarter": result.quarter,
        "friction_weight": result.weights.friction_weight,
        "inputs": dict(result.inputs),
        "scores": [
            {
                "pattern_id": s.pattern_id,
                "case_count": s.case_count,
                "transfer_index": s.transfer_index,
                "strict_index": s.strict_index,
                "outcomes": dict(s.outcomes),
            }
            for s in result.scores
        ],
    }


def render_ledger_row(result: RunResult) -> str:
    fm = _result_to_frontmatter(result)
    buf = io.StringIO()
    buf.write("---\n")
    yaml.safe_dump(fm, buf, sort_keys=False, default_flow_style=False)
    buf.write("---\n\n")
    buf.write(f"# Scoring run — {result.quarter}\n\n")
    buf.write(
        f"Per-pattern transfer index for {result.quarter}, computed from "
        f"{result.inputs['cases']} case(s) across {result.inputs['patterns']} "
        f"pattern(s) in the corpus. Friction weight in use: "
        f"{result.weights.friction_weight}.\n\n"
    )
    if not result.scores:
        buf.write("No patterns in the corpus.\n")
        return buf.getvalue()

    buf.write("| Pattern | Cases | Transfer index | Strict index |\n")
    buf.write("|---|---:|---:|---:|\n")
    for s in result.scores:
        ti = "—" if s.transfer_index is None else f"{s.transfer_index:.2f}"
        si = "—" if s.strict_index is None else f"{s.strict_index:.2f}"
        buf.write(f"| {s.pattern_id} | {s.case_count} | {ti} | {si} |\n")
    return buf.getvalue()


def write_ledger_row(result: RunResult, out_dir: Path) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{result.run_id}.md"
    out_path.write_text(render_ledger_row(result), encoding="utf-8")
    return out_path
