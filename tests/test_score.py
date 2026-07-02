from datetime import date
from pathlib import Path

import pytest

from procurement_pattern_library.loader import load_corpus
from procurement_pattern_library.score import (
    ScoreError,
    ScoreWeights,
    parse_quarter,
    render_ledger_row,
    score_quarter,
    write_ledger_row,
)


def test_parse_quarter_q2():
    start, end = parse_quarter("2026-Q2")
    assert start == date(2026, 4, 1)
    assert end == date(2026, 6, 30)


def test_parse_quarter_q4_year_boundary():
    start, end = parse_quarter("2026-Q4")
    assert start == date(2026, 10, 1)
    assert end == date(2026, 12, 31)


def test_parse_quarter_rejects_bad_input():
    with pytest.raises(ScoreError):
        parse_quarter("2026-Q5")
    with pytest.raises(ScoreError):
        parse_quarter("not-a-quarter")


def test_score_tiny_corpus(tiny_corpus: Path):
    corpus = load_corpus(tiny_corpus)
    result = score_quarter(corpus, "2026-Q2")
    by_id = {s.pattern_id: s for s in result.scores}
    # alpha: 1 clean + 1 friction → transfer 0.75, strict 0.5
    assert by_id["alpha"].transfer_index == 0.75
    assert by_id["alpha"].strict_index == 0.5
    assert by_id["alpha"].case_count == 2
    # beta: 1 did-not-transfer → transfer 0, strict 0
    assert by_id["beta"].transfer_index == 0.0
    assert by_id["beta"].strict_index == 0.0
    # gamma: 0 cases → null indices
    assert by_id["gamma"].transfer_index is None
    assert by_id["gamma"].strict_index is None


def test_friction_weight_changes_score(tiny_corpus: Path):
    corpus = load_corpus(tiny_corpus)
    r_default = score_quarter(corpus, "2026-Q2")
    r_strict = score_quarter(corpus, "2026-Q2", weights=ScoreWeights(friction_weight=0.0))
    alpha_default = next(s for s in r_default.scores if s.pattern_id == "alpha")
    alpha_strict = next(s for s in r_strict.scores if s.pattern_id == "alpha")
    assert alpha_default.transfer_index == 0.75
    assert alpha_strict.transfer_index == 0.5


def test_ledger_row_is_deterministic(tiny_corpus: Path):
    corpus = load_corpus(tiny_corpus)
    r1 = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    r2 = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    assert render_ledger_row(r1) == render_ledger_row(r2)


def test_write_ledger_row_creates_file(tiny_corpus: Path, tmp_path: Path):
    corpus = load_corpus(tiny_corpus)
    result = score_quarter(corpus, "2026-Q2", today=date(2026, 6, 22))
    out = write_ledger_row(result, tmp_path / "ledger" / "runs")
    assert out.exists()
    assert out.name == "2026-Q2-transfer-score.md"
    text = out.read_text(encoding="utf-8")
    assert "run_id: 2026-Q2-transfer-score" in text
    assert "friction_weight: 0.5" in text


def test_q1_case_excluded_from_q2_run(tmp_path: Path):
    """A case opened in Q1 does not show up in Q2 case counts."""
    p = tmp_path / "patterns"
    p.mkdir()
    (p / "alpha.md").write_text(
        """---
id: alpha
name: Alpha
canonical_statement: x
domains: [procurement]
created_at: '2026-01-01'
applications_dir: applications/
---
""",
        encoding="utf-8",
    )
    apps = p / "alpha" / "applications"
    apps.mkdir(parents=True)
    (apps / "q1.md").write_text(
        """---
id: q1
pattern_id: alpha
domain: procurement
upstream_artifact: repo://x/y.md
opened_at: '2026-03-15'
outcome: transferred-cleanly
---
""",
        encoding="utf-8",
    )
    corpus = load_corpus(tmp_path)
    result = score_quarter(corpus, "2026-Q2")
    assert result.inputs["cases"] == 0
    by_id = {s.pattern_id: s for s in result.scores}
    assert by_id["alpha"].case_count == 0


def test_quarter_membership_is_inclusive_at_both_edges(tmp_path: Path):
    """Cases opened on the first/last day of Q2 count; one day outside does not.

    Pins the inclusive comparison in _opened_in_quarter at both ends:
    04-01 and 06-30 are in, 03-31 and 07-01 are out.
    """
    p = tmp_path / "patterns"
    p.mkdir()
    (p / "alpha.md").write_text(
        """---
id: alpha
name: Alpha
canonical_statement: x
domains: [procurement]
created_at: '2026-01-01'
applications_dir: applications/
---
""",
        encoding="utf-8",
    )
    apps = p / "alpha" / "applications"
    apps.mkdir(parents=True)
    for cid, opened in [
        ("before", "2026-03-31"),
        ("start", "2026-04-01"),
        ("end", "2026-06-30"),
        ("after", "2026-07-01"),
    ]:
        (apps / f"{cid}.md").write_text(
            f"""---
id: {cid}
pattern_id: alpha
domain: procurement
upstream_artifact: repo://x/y.md
opened_at: '{opened}'
outcome: transferred-cleanly
---
""",
            encoding="utf-8",
        )
    corpus = load_corpus(tmp_path)
    result = score_quarter(corpus, "2026-Q2")
    # only the two boundary cases fall inside the quarter
    assert result.inputs["cases"] == 2
    by_id = {s.pattern_id: s for s in result.scores}
    assert by_id["alpha"].case_count == 2
