"""No-arg `show` verb: read the committed corpus and print a ranked,
readable transfer-signal table across every pattern, plus a headline
finding.

Unlike `score`, this does not filter by quarter. It folds every case
in the corpus into a per-pattern transfer index so a reader can open
the library and see, at a glance, which patterns are landing cleanly,
which land with friction, and which have no signal yet. Read-only,
offline.
"""

from __future__ import annotations

import io
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .loader import Corpus, load_corpus
from .score import ScoreWeights


@dataclass(frozen=True)
class PatternRow:
    pattern_id: str
    name: str
    case_count: int
    scored_count: int
    transfer_index: float | None
    strict_index: float | None
    outcomes: dict[str, int]


def _name_for(corpus: Corpus, pattern_id: str) -> str:
    for p in corpus.patterns:
        if p.id == pattern_id:
            return str(p.front_matter.get("name", pattern_id))
    return pattern_id


def summarize(corpus: Corpus, weights: ScoreWeights | None = None) -> list[PatternRow]:
    """Fold every case into a per-pattern row, ranked best-first."""
    weights = weights or ScoreWeights()

    by_pattern: dict[str, list] = {}
    for c in corpus.cases:
        by_pattern.setdefault(c.pattern_id, []).append(c)
    for p in corpus.patterns:
        by_pattern.setdefault(p.id, [])

    rows: list[PatternRow] = []
    for pid in sorted(by_pattern):
        outcomes: Counter[str] = Counter()
        for c in by_pattern[pid]:
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
            ti = None
            si = None
        else:
            ti = round(
                (
                    outcomes["transferred-cleanly"] * 1.0
                    + outcomes["transferred-with-friction"] * weights.friction_weight
                )
                / scored,
                4,
            )
            si = round(outcomes["transferred-cleanly"] / scored, 4)

        rows.append(
            PatternRow(
                pattern_id=pid,
                name=_name_for(corpus, pid),
                case_count=sum(outcomes.values()),
                scored_count=scored,
                transfer_index=ti,
                strict_index=si,
                outcomes={k: outcomes[k] for k in sorted(outcomes) if outcomes[k] > 0},
            )
        )

    rows.sort(
        key=lambda r: (
            -(r.transfer_index if r.transfer_index is not None else -1.0),
            -r.case_count,
            r.pattern_id,
        )
    )
    return rows


def _fmt(x: float | None) -> str:
    return "  -- " if x is None else f"{x:.2f}"


def render(corpus: Corpus, weights: ScoreWeights | None = None) -> str:
    rows = summarize(corpus, weights)
    buf = io.StringIO()
    buf.write("procurement pattern library - transfer signal across the corpus\n")
    buf.write("=" * 62 + "\n\n")

    total_cases = sum(r.case_count for r in rows)
    scored_cases = sum(r.scored_count for r in rows)
    buf.write(
        f"{len(rows)} pattern(s), {total_cases} application case(s) "
        f"({scored_cases} scored, {total_cases - scored_cases} pending).\n\n"
    )

    if not rows:
        buf.write("corpus is empty — no patterns under patterns/.\n")
        return buf.getvalue()

    name_w = max(len("pattern"), *(len(r.name) for r in rows))
    header = (
        f"  {'#':>2}  {'pattern'.ljust(name_w)}  {'cases':>5}  "
        f"{'transfer':>8}  {'strict':>6}"
    )
    buf.write(header + "\n")
    buf.write("  " + "-" * (len(header) - 2) + "\n")
    for i, r in enumerate(rows, 1):
        buf.write(
            f"  {i:>2}  {r.name.ljust(name_w)}  {r.case_count:>5}  "
            f"{_fmt(r.transfer_index):>8}  {_fmt(r.strict_index):>6}\n"
        )

    buf.write("\n")
    buf.write(_headline(rows) + "\n")
    return buf.getvalue()


def _headline(rows: list[PatternRow]) -> str:
    scored = [r for r in rows if r.transfer_index is not None]
    pending = [r for r in rows if r.transfer_index is None]

    if not scored:
        return (
            "headline: no pattern has a scored case yet — every application "
            "is still pending."
        )

    top = scored[0]
    gap = (
        top.transfer_index - top.strict_index
        if top.strict_index is not None
        else 0.0
    )
    parts = [
        f"headline: `{top.pattern_id}` leads at transfer index "
        f"{top.transfer_index:.2f} over {top.case_count} case(s)."
    ]
    if gap >= 0.1:
        parts.append(
            f"its strict index ({top.strict_index:.2f}) sits {gap:.2f} below — "
            f"it is landing, but with friction worth a refactor look."
        )
    if pending:
        names = ", ".join(f"`{r.pattern_id}`" for r in pending)
        parts.append(f"no signal yet for {names}.")
    return " ".join(parts)


def show(root: Path, weights: ScoreWeights | None = None) -> str:
    """Load the corpus at root and return the rendered ranked view."""
    corpus = load_corpus(root)
    return render(corpus, weights)
