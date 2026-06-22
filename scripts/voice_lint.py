"""Skeleton voice gate — warns on marketing language, does not fail.

The failing-gate hardening is queued in STATUS.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BANNED_WARN = {
    "world-class",
    "best-in-class",
    "synergy",
    "synergies",
    "leverage the power",
    "delight",
    "seamless",
    "revolutionary",
    "game-changing",
    "cutting-edge",
}


def scan_file(path: Path) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        lower = line.lower()
        for term in BANNED_WARN:
            if term in lower:
                hits.append((i, term))
    return hits


def main() -> int:
    total = 0
    targets = list((REPO_ROOT / "patterns").rglob("*.md"))
    targets += list((REPO_ROOT / "retros").rglob("*.md")) if (REPO_ROOT / "retros").exists() else []
    for path in sorted(targets):
        for line_no, term in scan_file(path):
            rel = path.relative_to(REPO_ROOT)
            print(f"WARN    {rel}:{line_no}: banned term {term!r}")
            total += 1
    print(f"scanned {len(targets)} file(s); {total} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
