"""Voice gate for checked-in pattern and retro Markdown."""

from __future__ import annotations

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

BANNED_FAIL = {
    "industry-leading",
    "best-of-breed",
    "paradigm shift",
}


def scan_file(path: Path, terms: set[str]) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        lower = line.lower()
        for term in sorted(terms):
            if term in lower:
                hits.append((i, term))
    return hits


def main(root: Path = REPO_ROOT) -> int:
    warnings = 0
    failures = 0
    targets = list((root / "patterns").rglob("*.md"))
    targets += list((root / "retros").rglob("*.md")) if (root / "retros").exists() else []
    for path in sorted(targets):
        rel = path.relative_to(root)
        for line_no, term in scan_file(path, BANNED_WARN):
            print(f"WARN    {rel}:{line_no}: banned term {term!r}")
            warnings += 1
        for line_no, term in scan_file(path, BANNED_FAIL):
            print(f"FAIL    {rel}:{line_no}: banned term {term!r}")
            failures += 1
    print(f"scanned {len(targets)} file(s); {warnings} warning(s); {failures} failure(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
