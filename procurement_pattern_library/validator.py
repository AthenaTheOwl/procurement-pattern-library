"""Schema enforcement + ninety-day outcome rule."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable

from .loader import Case, Corpus, Pattern

DOMAIN_ENUM = {"procurement", "supply-chain", "mechanism-design", "ai-build"}
OUTCOME_ENUM = {
    "transferred-cleanly",
    "transferred-with-friction",
    "did-not-transfer",
    "still-pending",
}
URI_PREFIXES = ("repo://", "file://", "https://")
ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

OUTCOME_WINDOW_DAYS = 90


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    path: Path
    message: str


@dataclass
class ValidationResult:
    issues: list[ValidationIssue] = field(default_factory=list)

    def add(self, severity: str, path: Path, message: str) -> None:
        self.issues.append(ValidationIssue(severity, path, message))

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class SchemaSet:
    pattern: dict[str, Any]
    case: dict[str, Any]
    retro: dict[str, Any]

    @classmethod
    def load(cls, schemas_dir: Path) -> "SchemaSet":
        return cls(
            pattern=json.loads((schemas_dir / "pattern.schema.json").read_text("utf-8")),
            case=json.loads((schemas_dir / "case.schema.json").read_text("utf-8")),
            retro=json.loads((schemas_dir / "retro.schema.json").read_text("utf-8")),
        )


def _check_required(fm: dict[str, Any], required: Iterable[str]) -> list[str]:
    return [f"missing required field: {f}" for f in required if f not in fm]


def _check_id(value: Any) -> str | None:
    if not isinstance(value, str) or not ID_RE.match(value):
        return f"id must be kebab-case, got {value!r}"
    return None


def _check_date(value: Any) -> str | None:
    if isinstance(value, date):
        return None
    if not isinstance(value, str) or not DATE_RE.match(value):
        return f"date must be YYYY-MM-DD, got {value!r}"
    try:
        date.fromisoformat(value)
    except ValueError:
        return f"date is not a valid calendar date: {value!r}"
    return None


def _coerce_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and DATE_RE.match(value):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _validate_pattern(p: Pattern, result: ValidationResult, seen_ids: set[str]) -> None:
    fm = p.front_matter
    for msg in _check_required(
        fm,
        ["id", "name", "canonical_statement", "domains", "created_at", "applications_dir"],
    ):
        result.add("error", p.path, msg)

    msg = _check_id(fm.get("id"))
    if msg:
        result.add("error", p.path, msg)

    pid = fm.get("id")
    if isinstance(pid, str):
        if pid in seen_ids:
            result.add("error", p.path, f"duplicate pattern id: {pid}")
        seen_ids.add(pid)
        if p.path.stem != pid:
            result.add(
                "error",
                p.path,
                f"filename stem {p.path.stem!r} does not match id {pid!r}",
            )

    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        result.add("error", p.path, "name must be a non-empty string")

    statement = fm.get("canonical_statement")
    if not isinstance(statement, str) or not statement.strip():
        result.add("error", p.path, "canonical_statement must be a non-empty string")

    domains = fm.get("domains")
    if not isinstance(domains, list) or not domains:
        result.add("error", p.path, "domains must be a non-empty list")
    else:
        for d in domains:
            if d not in DOMAIN_ENUM:
                result.add("error", p.path, f"domain {d!r} not in enum {sorted(DOMAIN_ENUM)}")

    msg = _check_date(fm.get("created_at"))
    if msg:
        result.add("error", p.path, msg)

    apps = fm.get("applications_dir")
    if apps != "applications/":
        result.add("error", p.path, f"applications_dir must be 'applications/', got {apps!r}")


def _validate_case(
    c: Case,
    result: ValidationResult,
    pattern_ids: set[str],
    today: date,
    seen_case_ids: set[tuple[str, str]],
) -> None:
    fm = c.front_matter
    for msg in _check_required(
        fm,
        ["id", "pattern_id", "domain", "upstream_artifact", "opened_at"],
    ):
        result.add("error", c.path, msg)

    cid = fm.get("id")
    msg = _check_id(cid)
    if msg:
        result.add("error", c.path, msg)

    pid = fm.get("pattern_id")
    msg = _check_id(pid)
    if msg:
        result.add("error", c.path, msg)

    if isinstance(pid, str):
        if pid != c.directory_pattern_id:
            result.add(
                "error",
                c.path,
                f"pattern_id {pid!r} does not match parent directory {c.directory_pattern_id!r}",
            )
        if pid not in pattern_ids:
            result.add("error", c.path, f"pattern_id {pid!r} has no matching pattern file")

    if isinstance(pid, str) and isinstance(cid, str):
        key = (pid, cid)
        if key in seen_case_ids:
            result.add("error", c.path, f"duplicate case id within pattern: {cid}")
        seen_case_ids.add(key)

    domain = fm.get("domain")
    if domain not in DOMAIN_ENUM:
        result.add("error", c.path, f"domain {domain!r} not in enum {sorted(DOMAIN_ENUM)}")

    uri = fm.get("upstream_artifact")
    if not isinstance(uri, str) or not uri.startswith(URI_PREFIXES):
        result.add(
            "error",
            c.path,
            f"upstream_artifact must start with one of {URI_PREFIXES}, got {uri!r}",
        )

    opened = fm.get("opened_at")
    msg = _check_date(opened)
    if msg:
        result.add("error", c.path, msg)

    outcome = fm.get("outcome")
    if outcome is not None and outcome not in OUTCOME_ENUM:
        result.add("error", c.path, f"outcome {outcome!r} not in enum {sorted(OUTCOME_ENUM)}")

    opened_date = _coerce_date(opened)
    if opened_date is not None:
        age = today - opened_date
        if age > timedelta(days=OUTCOME_WINDOW_DAYS) and not outcome:
            result.add(
                "error",
                c.path,
                f"case opened {age.days} days ago has empty outcome (limit {OUTCOME_WINDOW_DAYS})",
            )


def validate(corpus: Corpus, schemas: SchemaSet | None = None, today: date | None = None) -> ValidationResult:
    """Validate every pattern and case in the corpus.

    The schemas argument is accepted for forward-compat with a
    jsonschema-driven check; the v0.1 implementation hand-rolls
    the same rules and ignores the loaded schema bodies.
    """
    del schemas  # not used in v0.1; see DEC-PPL-001 and STATUS Known limits
    today = today or date.today()
    result = ValidationResult()
    seen_pattern_ids: set[str] = set()

    for p in corpus.patterns:
        _validate_pattern(p, result, seen_pattern_ids)

    pattern_ids = {p.id for p in corpus.patterns if p.id}
    seen_case_ids: set[tuple[str, str]] = set()
    for c in corpus.cases:
        _validate_case(c, result, pattern_ids, today, seen_case_ids)

    return result
