from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VOICE_LINT_PATH = REPO_ROOT / "scripts" / "voice_lint.py"

SPEC = importlib.util.spec_from_file_location("voice_lint", VOICE_LINT_PATH)
assert SPEC is not None
assert SPEC.loader is not None
voice_lint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(voice_lint)


def _write_pattern(root: Path, body: str) -> None:
    patterns = root / "patterns"
    patterns.mkdir(parents=True)
    (patterns / "alpha.md").write_text(body, encoding="utf-8")


def test_clean_markdown_exits_zero(tmp_path: Path, capsys):
    _write_pattern(tmp_path, "Plain procurement note.\n")

    assert voice_lint.main(tmp_path) == 0

    captured = capsys.readouterr()
    assert "FAIL" not in captured.out


def test_fail_term_in_pattern_exits_one(tmp_path: Path, capsys):
    _write_pattern(tmp_path, "This is not a paradigm shift.\n")

    assert voice_lint.main(tmp_path) == 1

    captured = capsys.readouterr()
    assert "FAIL" in captured.out
    assert "paradigm shift" in captured.out


def test_warn_only_term_exits_zero(tmp_path: Path, capsys):
    _write_pattern(tmp_path, "Avoid world-class phrasing here.\n")

    assert voice_lint.main(tmp_path) == 0

    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "FAIL" not in captured.out
