"""Markdown report writer for a scoring run.

The retro module prints a table to stdout. This module is the
persistent counterpart: it renders the same table plus a short prose
header into a checked-in Markdown report under `retros/<quarter>.md`.

Splitting stdout-printer from file-writer keeps each path narrow:
`retro.py` stays usable inside a pipeline or a notebook, and
`report.py` is what CI or the factory invokes to drop a report next to
the ledger row.
"""

from __future__ import annotations

from pathlib import Path

from .score import RunResult


def render_report(result: RunResult) -> str:
    """Render a Markdown report (with a header table) for one run."""
    lines: list[str] = []
    lines.append(f"# Quarterly retro — {result.quarter}")
    lines.append("")
    lines.append(
        f"Generated on {result.generated_at.isoformat()} from "
        f"{result.inputs['cases']} case(s) in {result.quarter} across "
        f"{result.inputs['patterns']} pattern(s) in the corpus."
    )
    lines.append("")
    lines.append(f"Friction weight in use: {result.weights.friction_weight}.")
    lines.append("")
    lines.append("## Per-pattern transfer index")
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
        lines.append("## No signal this quarter")
        lines.append("")
        for pid in sorted(no_signal):
            lines.append(f"- `{pid}` — no scored cases in {result.quarter}.")

    lines.append("")
    lines.append("## How to read this")
    lines.append("")
    lines.append(
        "Transfer index folds the friction-weighted outcomes into one "
        "number in `[0, 1]`. Strict index drops the friction credit. "
        "A wide gap between the two is a refactor signal — the pattern "
        "is landing but not cleanly. See `docs/METHODOLOGY.md` for the "
        "full scoring rule."
    )
    return "\n".join(lines) + "\n"


def write_report(result: RunResult, out_dir: Path) -> Path:
    """Write the rendered report to `<out_dir>/<quarter>.md`."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{result.quarter}.md"
    out_path.write_text(render_report(result), encoding="utf-8")
    return out_path
