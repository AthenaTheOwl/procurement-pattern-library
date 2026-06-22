from datetime import date
from pathlib import Path

from procurement_pattern_library.loader import load_corpus
from procurement_pattern_library.validator import validate


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


def test_checked_in_corpus_validates():
    """The repo's own seed corpus passes validation as of the run date."""
    root = Path(__file__).resolve().parent.parent
    corpus = load_corpus(root)
    result = validate(corpus, today=date(2026, 6, 22))
    assert result.ok, [f"{i.path}: {i.message}" for i in result.errors]
