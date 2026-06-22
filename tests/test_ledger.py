"""Tests for the JSONL ledger surface in `data/ledger/`."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from procurement_pattern_library.ledger import (
    JSONL_SCHEMA_VERSION,
    append_jsonl_row,
    iter_jsonl,
    read_jsonl_row,
    render_jsonl_row,
    write_jsonl_row,
)
from procurement_pattern_library.loader import load_corpus
from procurement_pattern_library.score import score_quarter


def test_render_jsonl_row_is_single_line(tiny_corpus: Path):
    corpus = load_corpus(tiny_corpus)
    result = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    line = render_jsonl_row(result)
    assert line.endswith("\n")
    assert line.count("\n") == 1
    parsed = json.loads(line)
    assert parsed["run_id"] == "2026-Q2-transfer-score"
    assert parsed["quarter"] == "2026-Q2"
    assert parsed["friction_weight"] == 0.5
    assert parsed["schema_version"] == JSONL_SCHEMA_VERSION


def test_write_jsonl_row_creates_file(tiny_corpus: Path, tmp_path: Path):
    corpus = load_corpus(tiny_corpus)
    result = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    out_dir = tmp_path / "data" / "ledger"
    out = write_jsonl_row(result, out_dir)
    assert out.exists()
    assert out.name == "2026-Q2-transfer-score.jsonl"
    rows = list(iter_jsonl(out))
    assert len(rows) == 1
    assert rows[0]["run_id"] == "2026-Q2-transfer-score"


def test_jsonl_round_trip(tiny_corpus: Path, tmp_path: Path):
    corpus = load_corpus(tiny_corpus)
    result = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    out = write_jsonl_row(result, tmp_path)
    restored = read_jsonl_row(out)
    assert restored.run_id == result.run_id
    assert restored.quarter == result.quarter
    assert restored.weights.friction_weight == result.weights.friction_weight
    assert restored.inputs == result.inputs
    assert {s.pattern_id for s in restored.scores} == {
        s.pattern_id for s in result.scores
    }


def test_append_jsonl_row_grows_aggregate(tiny_corpus: Path, tmp_path: Path):
    corpus = load_corpus(tiny_corpus)
    r1 = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    r2 = score_quarter(corpus, "2026-Q2", today=date(2026, 7, 1))
    target = tmp_path / "data" / "ledger" / "all-runs.jsonl"
    append_jsonl_row(r1, target)
    append_jsonl_row(r2, target)
    rows = list(iter_jsonl(target))
    assert len(rows) == 2


def test_read_jsonl_row_rejects_multi_row(tmp_path: Path, tiny_corpus: Path):
    corpus = load_corpus(tiny_corpus)
    result = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    target = tmp_path / "agg.jsonl"
    append_jsonl_row(result, target)
    append_jsonl_row(result, target)
    with pytest.raises(ValueError):
        read_jsonl_row(target)


def test_checked_in_ledger_row_is_valid_jsonl():
    """The committed `data/ledger/2026-Q2-transfer-score.jsonl` must parse."""
    repo_root = Path(__file__).resolve().parents[1]
    jsonl = repo_root / "data" / "ledger" / "2026-Q2-transfer-score.jsonl"
    assert jsonl.exists(), f"missing checked-in ledger row: {jsonl}"
    rows = list(iter_jsonl(jsonl))
    assert len(rows) == 1
    row = rows[0]
    assert row["run_id"] == "2026-Q2-transfer-score"
    assert row["quarter"] == "2026-Q2"
    assert isinstance(row["scores"], list)
    assert row["schema_version"] == JSONL_SCHEMA_VERSION
