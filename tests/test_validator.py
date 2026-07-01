from datetime import date, timedelta
from pathlib import Path

from procurement_pattern_library.loader import load_corpus
from procurement_pattern_library.validator import validate


def _pending_case_corpus(tmp_path: Path, opened: date) -> Path:
    """A one-pattern corpus with a single pending case opened on `opened`."""
    (tmp_path / "patterns").mkdir(parents=True)
    (tmp_path / "patterns" / "alpha.md").write_text(
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
    apps = tmp_path / "patterns" / "alpha" / "applications"
    apps.mkdir(parents=True)
    (apps / "pending.md").write_text(
        f"""---
id: pending
pattern_id: alpha
domain: procurement
upstream_artifact: repo://x/y.md
opened_at: '{opened.isoformat()}'
---
""",
        encoding="utf-8",
    )
    return tmp_path


def test_clean_corpus_validates(tiny_corpus: Path):
    corpus = load_corpus(tiny_corpus)
    result = validate(corpus, today=date(2026, 6, 22))
    assert result.ok, [i.message for i in result.errors]
    assert result.errors == []


def test_outcome_rule_flags_old_pending(tmp_path: Path):
    (tmp_path / "patterns").mkdir()
    (tmp_path / "patterns" / "alpha.md").write_text(
        """---
id: alpha
name: Alpha
canonical_statement: x
domains: [procurement]
created_at: '2026-01-01'
applications_dir: applications/
---

body
""",
        encoding="utf-8",
    )
    apps = tmp_path / "patterns" / "alpha" / "applications"
    apps.mkdir(parents=True)
    (apps / "stale.md").write_text(
        """---
id: stale
pattern_id: alpha
domain: procurement
upstream_artifact: repo://x/y.md
opened_at: '2026-01-01'
---

body
""",
        encoding="utf-8",
    )
    corpus = load_corpus(tmp_path)
    result = validate(corpus, today=date(2026, 6, 22))
    assert not result.ok
    assert any("empty outcome" in i.message for i in result.errors)


def test_recent_pending_does_not_flag(tmp_path: Path):
    (tmp_path / "patterns").mkdir()
    (tmp_path / "patterns" / "alpha.md").write_text(
        """---
id: alpha
name: Alpha
canonical_statement: x
domains: [procurement]
created_at: '2026-01-01'
applications_dir: applications/
---

body
""",
        encoding="utf-8",
    )
    apps = tmp_path / "patterns" / "alpha" / "applications"
    apps.mkdir(parents=True)
    (apps / "fresh.md").write_text(
        """---
id: fresh
pattern_id: alpha
domain: procurement
upstream_artifact: repo://x/y.md
opened_at: '2026-06-01'
---

body
""",
        encoding="utf-8",
    )
    corpus = load_corpus(tmp_path)
    result = validate(corpus, today=date(2026, 6, 22))
    assert result.ok


def test_case_pattern_id_must_match_directory(tmp_path: Path):
    (tmp_path / "patterns").mkdir()
    (tmp_path / "patterns" / "alpha.md").write_text(
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
    apps = tmp_path / "patterns" / "alpha" / "applications"
    apps.mkdir(parents=True)
    (apps / "bad.md").write_text(
        """---
id: bad
pattern_id: beta
domain: procurement
upstream_artifact: repo://x/y.md
opened_at: '2026-06-01'
outcome: transferred-cleanly
---
""",
        encoding="utf-8",
    )
    corpus = load_corpus(tmp_path)
    result = validate(corpus, today=date(2026, 6, 22))
    assert any("does not match parent directory" in i.message for i in result.errors)


def test_bad_uri_prefix_is_error(tmp_path: Path):
    (tmp_path / "patterns").mkdir()
    (tmp_path / "patterns" / "alpha.md").write_text(
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
    apps = tmp_path / "patterns" / "alpha" / "applications"
    apps.mkdir(parents=True)
    (apps / "bad.md").write_text(
        """---
id: bad
pattern_id: alpha
domain: procurement
upstream_artifact: gopher://x/y.md
opened_at: '2026-06-01'
outcome: transferred-cleanly
---
""",
        encoding="utf-8",
    )
    corpus = load_corpus(tmp_path)
    result = validate(corpus, today=date(2026, 6, 22))
    assert any("upstream_artifact" in i.message for i in result.errors)


def test_pending_exactly_at_window_edge_does_not_flag(tmp_path: Path):
    """A pending case opened exactly 90 days ago is inside the limit.

    Pins the `>` (not `>=`) comparison at the boundary: age == 90 is fine.
    """
    today = date(2026, 6, 22)
    root = _pending_case_corpus(tmp_path, today - timedelta(days=90))
    result = validate(load_corpus(root), today=today)
    assert result.ok, [i.message for i in result.errors]


def test_window_length_is_ninety_days(tmp_path: Path):
    """91 days flags, 89 days does not — pins the window length at 90.

    A shorter limit (e.g. 45 or 60) would flag the 89-day case; a longer
    limit would clear the 91-day case. Only 90 splits these two.
    """
    today = date(2026, 6, 22)

    over = _pending_case_corpus(tmp_path / "over", today - timedelta(days=91))
    over_result = validate(load_corpus(over), today=today)
    assert not over_result.ok
    assert any("empty outcome" in i.message for i in over_result.errors)

    under = _pending_case_corpus(tmp_path / "under", today - timedelta(days=89))
    under_result = validate(load_corpus(under), today=today)
    assert under_result.ok, [i.message for i in under_result.errors]


def test_checked_in_corpus_validates():
    """The repo's own seed corpus passes validation as of the run date."""
    root = Path(__file__).resolve().parent.parent
    corpus = load_corpus(root)
    result = validate(corpus, today=date(2026, 6, 22))
    assert result.ok, [f"{i.path}: {i.message}" for i in result.errors]
