import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _run(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "procurement_pattern_library", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def test_cli_validate_on_seed_corpus():
    r = _run("validate")
    assert r.returncode == 0, r.stdout + r.stderr


def test_cli_show_no_arg():
    r = _run("show")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "transfer signal" in r.stdout
    assert "headline:" in r.stdout
    # every seed pattern's name shows up in the ranked table
    assert "Dual-source the critical path" in r.stdout
    assert "transfer" in r.stdout and "strict" in r.stdout


def test_cli_score_no_write(tmp_path: Path):
    r = _run("score", "--quarter", "2026-Q2", "--no-write")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "2026-Q2" in r.stdout


def test_cli_retro_from_ledger():
    r = _run(
        "retro",
        "--quarter",
        "2026-Q2",
        "--from-ledger",
        str(REPO_ROOT / "ledger" / "runs" / "2026-Q2-transfer-score.md"),
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Retro" in r.stdout
    assert "dual-source" in r.stdout


def test_cli_retro_from_missing_ledger_exits_2(tmp_path: Path):
    r = _run(
        "retro",
        "--quarter",
        "2026-Q2",
        "--from-ledger",
        str(tmp_path / "does-not-exist.md"),
    )
    assert r.returncode == 2, r.stdout + r.stderr
    assert r.stderr.startswith("ERROR: retro:")
