"""procurement_pattern_library: typed pattern corpus + scoring CLI."""

__version__ = "0.1.0"

from .loader import Corpus, Pattern, Case, load_corpus, parse_front_matter
from .validator import ValidationIssue, ValidationResult, validate
from .score import RunResult, PatternScore, ScoreWeights, score_quarter, write_ledger_row
from .ledger import (
    append_jsonl_row,
    iter_jsonl,
    read_jsonl_row,
    render_jsonl_row,
    write_jsonl_row,
)
from .report import render_report, write_report
from .show import PatternRow, summarize, show

__all__ = [
    "__version__",
    "Corpus",
    "Pattern",
    "Case",
    "load_corpus",
    "parse_front_matter",
    "ValidationIssue",
    "ValidationResult",
    "validate",
    "RunResult",
    "PatternScore",
    "ScoreWeights",
    "score_quarter",
    "write_ledger_row",
    "append_jsonl_row",
    "iter_jsonl",
    "read_jsonl_row",
    "render_jsonl_row",
    "write_jsonl_row",
    "render_report",
    "write_report",
    "PatternRow",
    "summarize",
    "show",
]
