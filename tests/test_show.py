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
