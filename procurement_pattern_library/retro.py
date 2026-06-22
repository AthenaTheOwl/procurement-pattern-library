"""Render a scoring run as a Markdown table to stdout (v0.1)."""

from __future__ import annotations

import sys
from pathlib import Path

from .loader import parse_front_matter
from .score import RunResult, PatternScore, ScoreWeights


def render(result: RunResult) -> str:
    lines: list[str] = []
    lines.append(f"# Retro — {result.quarter}")
    lines.append("")
    lines.append(
        f"Computed {result.generated_at.isoformat()} from "
        f"{result.inputs['cases']} case(s) across "
        f"{result.inputs['patterns']} pattern(s). Friction weight: "
        f"{result.weights.friction_weight}."
    )
    lines.append("")
    lines.append("| Pattern | Cases | Transfer index | Strict index |")
    lines.append("|---|---:|---:|---:|")
    for s in result.scores:
        ti = "—" if s.transfer_index is None else f"{s.transfer_index:.2f}"
        si = "—" if s.strict_index is None else f"{s.strict_index:.2f}"
        lines.append(f"| {s.pattern_id} | {s.case_count} | {ti} | {si} |")
    no_signal = [s.pattern_id for s in result.scores if s.transfer_index is None]
    if no_signal:
        lines.append("")
        lines.append(
            "No signal this quarter: " + ", ".join(sorted(no_signal)) + "."
        )
    return "\n".join(lines) + "\n"


def from_ledger_row(path: Path) -> RunResult:
    """Reverse of render_ledger_row: parse a ledger row back into a RunResult."""
    from datetime import date
    text = Path(path).read_text(encoding="utf-8")
    fm, _ = parse_front_matter(text)
    scores = [
        PatternScore(
            pattern_id=s["pattern_id"],
            case_count=s["case_count"],
            transfer_index=s.get("transfer_index"),
            strict_index=s.get("strict_index"),
            outcomes=dict(s.get("outcomes", {})),
        )
        for s in fm.get("scores", [])
    ]
    return RunResult(
        run_id=fm["run_id"],
        generated_at=date.fromisoformat(fm["generated_at"]),
        quarter=fm["quarter"],
        weights=ScoreWeights(friction_weight=float(fm["friction_weight"])),
        inputs=dict(fm["inputs"]),
        scores=scores,
    )


def print_retro(result: RunResult, stream=None) -> None:
    (stream or sys.stdout).write(render(result))
