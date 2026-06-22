"""Ledger surfaces: JSONL row writer + reader for `data/ledger/`.

Two ledger surfaces exist side by side. The Markdown row under
`ledger/runs/<run-id>.md` (written by `score.write_ledger_row`) is for
human readers. The JSONL row under `data/ledger/<run-id>.jsonl` (this
module) is for downstream tooling — a single JSON object per line so a
later run can append without rewriting the file.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterator

from .score import PatternScore, RunResult, ScoreWeights

JSONL_SCHEMA_VERSION = 1


def _result_to_jsonl_record(result: RunResult) -> dict:
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
        "schema_version": JSONL_SCHEMA_VERSION,
    }


def render_jsonl_row(result: RunResult) -> str:
    """Return a single JSONL line (with trailing newline) for a run."""
    record = _result_to_jsonl_record(result)
    return json.dumps(record, sort_keys=False, ensure_ascii=False) + "\n"


def write_jsonl_row(result: RunResult, out_dir: Path) -> Path:
    """Write a one-line JSONL file at `<out_dir>/<run-id>.jsonl`.

    The file is overwritten if it already exists. A scoring run is
    idempotent for a given (quarter, corpus, weights) tuple, so
    overwriting is the right behavior; the Markdown row in
    `ledger/runs/` lets a human spot drift between two runs.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{result.run_id}.jsonl"
    out_path.write_text(render_jsonl_row(result), encoding="utf-8")
    return out_path


def append_jsonl_row(result: RunResult, jsonl_path: Path) -> Path:
    """Append a single JSON line to an existing JSONL file.

    Used by scripts that aggregate many runs into one file (for
    example, `data/ledger/all-runs.jsonl`). The per-run file written by
    `write_jsonl_row` is the canonical, deterministic surface; this
    helper is for downstream rollups.
    """
    jsonl_path = Path(jsonl_path)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as fh:
        fh.write(render_jsonl_row(result))
    return jsonl_path


def iter_jsonl(jsonl_path: Path) -> Iterator[dict]:
    """Yield one parsed dict per non-empty line of a JSONL file."""
    jsonl_path = Path(jsonl_path)
    with jsonl_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def read_jsonl_row(jsonl_path: Path) -> RunResult:
    """Read a single-row JSONL ledger file and rebuild a `RunResult`.

    Raises `ValueError` if the file has zero rows or more than one.
    Use `iter_jsonl` to walk a multi-row aggregate file.
    """
    rows = list(iter_jsonl(jsonl_path))
    if not rows:
        raise ValueError(f"no rows in {jsonl_path}")
    if len(rows) > 1:
        raise ValueError(
            f"{jsonl_path} has {len(rows)} rows; use iter_jsonl for aggregates"
        )
    return _record_to_result(rows[0])


def _record_to_result(record: dict) -> RunResult:
    scores = [
        PatternScore(
            pattern_id=s["pattern_id"],
            case_count=s["case_count"],
            transfer_index=s.get("transfer_index"),
            strict_index=s.get("strict_index"),
            outcomes=dict(s.get("outcomes", {})),
        )
        for s in record.get("scores", [])
    ]
    return RunResult(
        run_id=record["run_id"],
        generated_at=date.fromisoformat(record["generated_at"]),
        quarter=record["quarter"],
        weights=ScoreWeights(friction_weight=float(record["friction_weight"])),
        inputs=dict(record["inputs"]),
        scores=scores,
    )
