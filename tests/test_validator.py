from datetime import date, timedelta
from pathlib import Path

import pytest

from procurement_pattern_library.loader import load_corpus
from procurement_pattern_library.validator import OUTCOME_RULE, validate


def _pending_case_corpus(tmp_path: Path, opened: date, outcome: str | None = None) -> Path:
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
{"" if outcome is None else f"outcome: '{outcome}'"}
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


@pytest.mark.parametrize(("age_days", "flags"), [(89, False), (90, False), (91, True)])
def test_still_pending_counts_as_unresolved(tmp_path: Path, age_days: int, flags: bool):
    """`still-pending` past the window fails like an empty outcome.

    DEC-PPL-001: a pending case older than ninety days is an invariant
    violation, not a retro entry. 89 and 90 days pass; 91 days fails.
    """
    today = date(2026, 10, 19)
    root = _pending_case_corpus(tmp_path, today - timedelta(days=age_days), outcome="still-pending")
    result = validate(load_corpus(root), today=today)
    if flags:
        assert len(result.errors) == 1
        assert OUTCOME_RULE in result.errors[0].message
        assert f"{age_days} days ago" in result.errors[0].message
        assert "'still-pending'" in result.errors[0].message
    else:
        assert result.ok, [i.message for i in result.errors]


def test_measured_outcome_past_window_does_not_flag(tmp_path: Path):
    today = date(2026, 10, 19)
    root = _pending_case_corpus(
        tmp_path, today - timedelta(days=150), outcome="transferred-with-friction"
    )
    result = validate(load_corpus(root), today=today)
    assert result.ok, [i.message for i in result.errors]


def test_empty_outcome_error_names_the_rule(tmp_path: Path):
    """scripts/validate_outcomes.py selects errors by OUTCOME_RULE."""
    today = date(2026, 10, 19)
    root = _pending_case_corpus(tmp_path, today - timedelta(days=91))
    result = validate(load_corpus(root), today=today)
    assert any(OUTCOME_RULE in i.message and "empty outcome" in i.message for i in result.errors)


def test_checked_in_corpus_validates():
    """The repo's own seed corpus passes validation as of the run date."""
    root = Path(__file__).resolve().parent.parent
    corpus = load_corpus(root)
    result = validate(corpus, today=date(2026, 6, 22))
    assert result.ok, [f"{i.path}: {i.message}" for i in result.errors]


PROSPECTIVE_CASE = {
    "id": "fallback-drill",
    "pattern_id": "dual-source",
    "domain": "ai-build",
    "upstream_artifact": "repo://x/y.md",
    "opened_at": "2026-10-01",
    "expected_mechanism": "A warm fallback absorbs a primary outage.",
    "failure_context": "Fallback output shape diverges from the primary.",
    "disconfirming_result": "Held-out case misses the quality threshold on failover.",
    "observation_window_days": 60,
}


def _case_schema_validator():
    import json

    from jsonschema import Draft202012Validator

    root = Path(__file__).resolve().parent.parent
    schema = json.loads((root / "schemas" / "case.schema.json").read_text("utf-8"))
    return Draft202012Validator(schema)


def test_case_schema_accepts_optional_prospective_fields():
    validator = _case_schema_validator()
    assert list(validator.iter_errors(PROSPECTIVE_CASE)) == []
    required = ("id", "pattern_id", "domain", "upstream_artifact", "opened_at")
    legacy = {k: PROSPECTIVE_CASE[k] for k in required}
    assert list(validator.iter_errors(legacy)) == []


@pytest.mark.parametrize(
    ("window", "keyword"), [(0, "minimum"), (91, "maximum"), ("60", "type")]
)
def test_case_schema_caps_observation_window_at_ninety(window, keyword):
    validator = _case_schema_validator()
    assert list(validator.iter_errors(dict(PROSPECTIVE_CASE, observation_window_days=60))) == []
    record = dict(PROSPECTIVE_CASE, observation_window_days=window)
    errors = [(e.validator, list(e.path)) for e in validator.iter_errors(record)]
    assert errors == [(keyword, ["observation_window_days"])]


def _prospective_corpus(tmp_path: Path, extra: str) -> Path:
    root = _pending_case_corpus(tmp_path, date(2026, 10, 1))
    case = root / "patterns" / "alpha" / "applications" / "pending.md"
    head, rest = case.read_text("utf-8").split("\n", 1)
    case.write_text(f"{head}\n{extra}{rest}", encoding="utf-8")
    return root


def test_validator_accepts_prospective_fields(tmp_path: Path):
    root = _prospective_corpus(
        tmp_path,
        "expected_mechanism: warm fallback absorbs outage\n"
        "failure_context: output shapes diverge\n"
        "disconfirming_result: held-out case misses threshold\n"
        "observation_window_days: 90\n",
    )
    result = validate(load_corpus(root), today=date(2026, 10, 19))
    assert result.ok, [i.message for i in result.errors]


def test_validator_accepts_integral_float_window_like_schema(tmp_path: Path):
    """The schema's integer type accepts 60.0, so the validator does too."""
    record = dict(PROSPECTIVE_CASE, observation_window_days=60.0)
    assert list(_case_schema_validator().iter_errors(record)) == []
    root = _prospective_corpus(tmp_path, "observation_window_days: 60.0\n")
    result = validate(load_corpus(root), today=date(2026, 10, 19))
    assert result.ok, [i.message for i in result.errors]


@pytest.mark.parametrize(
    ("extra", "needle"),
    [
        ("observation_window_days: 120\n", "observation_window_days"),
        ("observation_window_days: true\n", "observation_window_days"),
        ("observation_window_days: 60.5\n", "observation_window_days"),
        ("expected_mechanism: ''\n", "expected_mechanism"),
    ],
)
def test_validator_rejects_bad_prospective_fields(tmp_path: Path, extra: str, needle: str):
    root = _prospective_corpus(tmp_path, extra)
    result = validate(load_corpus(root), today=date(2026, 10, 19))
    assert any(needle in i.message for i in result.errors)
