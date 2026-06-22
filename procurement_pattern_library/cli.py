"""Argparse-driven CLI: validate, score, retro."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from .loader import LoaderError, load_corpus
from .score import ScoreError, ScoreWeights, score_quarter, write_ledger_row
from .retro import from_ledger_row, print_retro, render
from .validator import validate


def _add_root(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repo root (default: current working directory).",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="procurement-pattern-library",
        description="Validate, score, and roll up the typed pattern corpus.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Parse + schema-check + outcome rule.")
    _add_root(v)

    s = sub.add_parser("score", help="Compute per-pattern transfer index for a quarter.")
    _add_root(s)
    s.add_argument("--quarter", required=True, help="e.g. 2026-Q2")
    s.add_argument(
        "--friction-weight",
        type=float,
        default=0.5,
        help="Weight on transferred-with-friction (default: 0.5).",
    )
    s.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Override ledger output dir (default: <root>/ledger/runs).",
    )
    s.add_argument(
        "--no-write",
        action="store_true",
        help="Compute the score but do not write a ledger row.",
    )

    r = sub.add_parser("retro", help="Print a Markdown retro to stdout.")
    _add_root(r)
    r.add_argument("--quarter", required=True, help="e.g. 2026-Q2")
    r.add_argument(
        "--from-ledger",
        type=Path,
        default=None,
        help="Read a ledger row file instead of recomputing.",
    )

    return parser


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        corpus = load_corpus(args.root)
    except LoaderError as e:
        print(f"ERROR: loader: {e}", file=sys.stderr)
        return 2
    result = validate(corpus, schemas=None, today=date.today())
    for issue in result.issues:
        rel = issue.path
        try:
            rel = issue.path.relative_to(args.root)
        except ValueError:
            pass
        print(f"{issue.severity.upper():7} {rel}: {issue.message}")
    print(
        f"validated {len(corpus.patterns)} pattern(s), "
        f"{len(corpus.cases)} case(s); "
        f"{len(result.errors)} error(s), {len(result.warnings)} warning(s)."
    )
    return 0 if result.ok else 1


def cmd_score(args: argparse.Namespace) -> int:
    try:
        corpus = load_corpus(args.root)
        weights = ScoreWeights(friction_weight=args.friction_weight)
        result = score_quarter(corpus, args.quarter, weights=weights)
    except (LoaderError, ScoreError) as e:
        print(f"ERROR: score: {e}", file=sys.stderr)
        return 2

    if args.no_write:
        print(render(result))
        return 0

    out_dir = args.out or (args.root / "ledger" / "runs")
    path = write_ledger_row(result, out_dir)
    try:
        rel = path.relative_to(args.root)
    except ValueError:
        rel = path
    print(f"wrote {rel}")
    return 0


def cmd_retro(args: argparse.Namespace) -> int:
    if args.from_ledger:
        result = from_ledger_row(args.from_ledger)
    else:
        try:
            corpus = load_corpus(args.root)
            result = score_quarter(corpus, args.quarter)
        except (LoaderError, ScoreError) as e:
            print(f"ERROR: retro: {e}", file=sys.stderr)
            return 2
    print_retro(result)
    return 0


DISPATCH = {
    "validate": cmd_validate,
    "score": cmd_score,
    "retro": cmd_retro,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return DISPATCH[args.cmd](args)
