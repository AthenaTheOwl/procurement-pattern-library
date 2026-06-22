"""Tests for the persistent Markdown report writer."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from procurement_pattern_library.loader import load_corpus
from procurement_pattern_library.report import render_report, write_report
from procurement_pattern_library.score import score_quarter


def test_render_report_includes_per_pattern_table(tiny_corpus: Path):
    corpus = load_corpus(tiny_corpus)
    result = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    text = render_report(result)
    assert "# Quarterly retro — 2026-Q2" in text
    assert "## Per-pattern transfer index" in text
    assert "alpha" in text
    assert "Friction weight in use: 0.5" in text


def test_render_report_flags_no_signal(tiny_corpus: Path):
    """`gamma` has no cases this quarter, so it must show up in the no-signal section."""
    corpus = load_corpus(tiny_corpus)
    result = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    text = render_report(result)
    assert "## No signal this quarter" in text
    assert "gamma" in text


def test_write_report_uses_quarter_filename(tiny_corpus: Path, tmp_path: Path):
    corpus = load_corpus(tiny_corpus)
    result = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    out_dir = tmp_path / "retros"
    out = write_report(result, out_dir)
    assert out.exists()
    assert out.name == "2026-Q2.md"
    assert out.read_text(encoding="utf-8").startswith("# Quarterly retro — 2026-Q2")
