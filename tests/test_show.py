from pathlib import Path

from procurement_pattern_library.loader import load_corpus
from procurement_pattern_library.show import summarize, render, show


def test_summarize_ranks_best_first(tiny_corpus: Path):
    corpus = load_corpus(tiny_corpus)
    rows = summarize(corpus)
    # alpha: 1 clean + 1 friction -> 0.75 ; beta: 1 did-not-transfer -> 0.0
    # gamma: no cases -> None (sorts last)
    ids = [r.pattern_id for r in rows]
    assert ids == ["alpha", "beta", "gamma"]
    alpha = rows[0]
    assert alpha.transfer_index == 0.75
    assert alpha.strict_index == 0.5
    assert rows[-1].pattern_id == "gamma"
    assert rows[-1].transfer_index is None


def test_render_has_headline_and_table(tiny_corpus: Path):
    out = show(tiny_corpus)
    assert "transfer signal across the corpus" in out
    assert "headline:" in out
    # pending pattern with no scored case is called out
    assert "`gamma`" in out
    assert "3 pattern(s)" in out


def test_show_empty_corpus(tmp_path: Path):
    out = show(tmp_path)
    assert "0 pattern(s)" in out
    assert "no pattern" in out.lower() or "empty" in out.lower()


def _one_pattern_corpus(tmp_path: Path, outcomes: list[str]) -> Path:
    """A single-pattern corpus with one case per outcome in `outcomes`."""
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
    for i, outcome in enumerate(outcomes):
        (apps / f"case-{i}.md").write_text(
            f"""---
id: case-{i}
pattern_id: alpha
domain: procurement
upstream_artifact: repo://x/y.md
opened_at: '2026-05-01'
outcome: {outcome}
---
""",
            encoding="utf-8",
        )
    return tmp_path


def test_headline_calls_out_friction_gap_over_threshold(tmp_path: Path):
    """transfer 0.75 vs strict 0.5 (gap 0.25) trips the refactor-look line.

    Pins the `>= 0.1` threshold: a gap this wide must surface the sentence.
    """
    out = show(_one_pattern_corpus(tmp_path, ["transferred-cleanly",
                                              "transferred-with-friction"]))
    assert "friction worth a refactor look" in out


def test_headline_omits_friction_gap_when_all_clean(tmp_path: Path):
    """gap 0.0 (all clean) leaves the refactor-look line out."""
    out = show(_one_pattern_corpus(tmp_path, ["transferred-cleanly",
                                              "transferred-cleanly"]))
    assert "friction worth a refactor look" not in out
