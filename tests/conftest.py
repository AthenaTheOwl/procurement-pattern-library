"""Build a small synthetic corpus on disk for unit tests."""

from __future__ import annotations

from pathlib import Path

import pytest


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def tiny_corpus(tmp_path: Path) -> Path:
    """Three-pattern, four-case corpus under a fresh tmp_path."""
    root = tmp_path

    _write(
        root / "patterns" / "alpha.md",
        """---
id: alpha
name: Alpha pattern
canonical_statement: First test pattern.
domains: [procurement]
created_at: '2026-01-01'
applications_dir: applications/
---

body
""",
    )
    _write(
        root / "patterns" / "alpha" / "applications" / "case-1.md",
        """---
id: case-1
pattern_id: alpha
domain: procurement
upstream_artifact: repo://example/DEC-001.md
opened_at: '2026-04-15'
outcome: transferred-cleanly
---

body
""",
    )
    _write(
        root / "patterns" / "alpha" / "applications" / "case-2.md",
        """---
id: case-2
pattern_id: alpha
domain: ai-build
upstream_artifact: repo://example/DEC-002.md
opened_at: '2026-05-01'
outcome: transferred-with-friction
---

body
""",
    )

    _write(
        root / "patterns" / "beta.md",
        """---
id: beta
name: Beta pattern
canonical_statement: Second test pattern.
domains: [supply-chain, ai-build]
created_at: '2026-01-02'
applications_dir: applications/
---

body
""",
    )
    _write(
        root / "patterns" / "beta" / "applications" / "case-1.md",
        """---
id: case-1
pattern_id: beta
domain: ai-build
upstream_artifact: repo://example/DEC-003.md
opened_at: '2026-05-20'
outcome: did-not-transfer
---

body
""",
    )

    _write(
        root / "patterns" / "gamma.md",
        """---
id: gamma
name: Gamma pattern
canonical_statement: Third test pattern.
domains: [mechanism-design]
created_at: '2026-01-03'
applications_dir: applications/
---

body
""",
    )
    return root
