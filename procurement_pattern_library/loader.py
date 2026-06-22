"""Walk the corpus, parse YAML front-matter into dataclasses."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

FRONT_MATTER_RE = re.compile(
    r"\A\s*---\s*\n(?P<fm>.*?)\n---\s*\n?(?P<body>.*)\Z",
    re.DOTALL,
)


class LoaderError(ValueError):
    """A file could not be parsed into the expected shape."""


@dataclass(frozen=True)
class Pattern:
    front_matter: dict[str, Any]
    body: str
    path: Path

    @property
    def id(self) -> str:
        return str(self.front_matter.get("id", ""))


@dataclass(frozen=True)
class Case:
    front_matter: dict[str, Any]
    body: str
    path: Path
    directory_pattern_id: str

    @property
    def id(self) -> str:
        return str(self.front_matter.get("id", ""))

    @property
    def pattern_id(self) -> str:
        return str(self.front_matter.get("pattern_id", ""))


@dataclass(frozen=True)
class Corpus:
    patterns: list[Pattern] = field(default_factory=list)
    cases: list[Case] = field(default_factory=list)
    root: Path = Path(".")


def parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    """Split a Markdown document into (front_matter_dict, body).

    Raises LoaderError if the document is missing a front-matter
    block or if the block is not valid YAML.
    """
    m = FRONT_MATTER_RE.match(text)
    if not m:
        raise LoaderError("missing front-matter fence")
    fm_text = m.group("fm")
    body = m.group("body")
    try:
        fm = yaml.safe_load(fm_text)
    except yaml.YAMLError as e:
        raise LoaderError(f"invalid YAML in front-matter: {e}") from e
    if not isinstance(fm, dict):
        raise LoaderError("front-matter must be a mapping")
    return fm, body


def load_corpus(root: Path) -> Corpus:
    """Walk root/patterns/ and return parsed patterns and cases.

    A pattern file is any *.md directly under patterns/. A case
    file is any *.md under patterns/<pattern-id>/applications/.
    The loader rejects a case whose declared pattern_id does not
    match its parent directory.
    """
    root = Path(root)
    patterns_dir = root / "patterns"
    patterns: list[Pattern] = []
    cases: list[Case] = []

    if not patterns_dir.exists():
        return Corpus(patterns=patterns, cases=cases, root=root)

    for entry in sorted(patterns_dir.iterdir()):
        if entry.is_file() and entry.suffix == ".md":
            text = entry.read_text(encoding="utf-8")
            fm, body = parse_front_matter(text)
            patterns.append(Pattern(front_matter=fm, body=body, path=entry))

    for entry in sorted(patterns_dir.iterdir()):
        if not entry.is_dir():
            continue
        apps = entry / "applications"
        if not apps.is_dir():
            continue
        for case_file in sorted(apps.iterdir()):
            if not (case_file.is_file() and case_file.suffix == ".md"):
                continue
            text = case_file.read_text(encoding="utf-8")
            fm, body = parse_front_matter(text)
            cases.append(
                Case(
                    front_matter=fm,
                    body=body,
                    path=case_file,
                    directory_pattern_id=entry.name,
                )
            )

    return Corpus(patterns=patterns, cases=cases, root=root)
