"""Streamlit browser for the procurement pattern library.

Reads the committed corpus (patterns/*.md + their application cases)
directly from disk, paths relative to this file. No network, no
secrets. Mirrors the `show` verb: a ranked transfer-signal table plus
a per-pattern drill-down.
"""

from __future__ import annotations

from pathlib import Path
from statistics import median

import pandas as pd
import streamlit as st

from datetime import date

from procurement_pattern_library.loader import (
    Case,
    Corpus,
    LoaderError,
    load_corpus,
    parse_front_matter,
)
from procurement_pattern_library.score import ScoreWeights
from procurement_pattern_library.show import summarize
from procurement_pattern_library.validator import validate

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="procurement pattern library", layout="wide")
st.title("procurement pattern library")
st.caption(
    "typed procurement / mechanism-design patterns, each scored by how "
    "cleanly it transferred into ai-build work. read-only view of the "
    "committed corpus."
)

if not (ROOT / "patterns").is_dir():
    st.warning("no patterns/ directory found next to this app — corpus is missing.")
    st.stop()

corpus = load_corpus(ROOT)
if not corpus.patterns:
    st.warning("the corpus has no patterns yet.")
    st.stop()

friction = st.slider(
    "friction weight (credit given to a transfer that landed with friction)",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.05,
)

rows = summarize(corpus, ScoreWeights(friction_weight=friction))

total_cases = sum(r.case_count for r in rows)
scored_cases = sum(r.scored_count for r in rows)
scored_rows = [r for r in rows if r.transfer_index is not None]

c1, c2, c3 = st.columns(3)
c1.metric("patterns", len(rows))
c2.metric("application cases", total_cases)
c3.metric(
    "median transfer index",
    f"{median([r.transfer_index for r in scored_rows]):.2f}"
    if scored_rows
    else "--",
)

if scored_rows:
    top = scored_rows[0]
    gap = (
        top.transfer_index - top.strict_index
        if top.strict_index is not None
        else 0.0
    )
    msg = (
        f"`{top.pattern_id}` leads at transfer index "
        f"{top.transfer_index:.2f} over {top.case_count} case(s)."
    )
    if gap >= 0.1:
        msg += (
            f" its strict index ({top.strict_index:.2f}) sits {gap:.2f} below — "
            f"landing, but with friction worth a refactor look."
        )
    st.info(msg)
else:
    st.info("no pattern has a scored case yet — every application is still pending.")

st.subheader("transfer signal across the corpus")
df = pd.DataFrame(
    [
        {
            "pattern": r.name,
            "id": r.pattern_id,
            "cases": r.case_count,
            "transfer index": r.transfer_index,
            "strict index": r.strict_index,
        }
        for r in rows
    ]
)
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("drill into a pattern")
choice = st.selectbox(
    "pattern",
    options=[r.pattern_id for r in rows],
    format_func=lambda pid: next(r.name for r in rows if r.pattern_id == pid),
)
row = next(r for r in rows if r.pattern_id == choice)

d1, d2 = st.columns(2)
d1.metric("transfer index", f"{row.transfer_index:.2f}" if row.transfer_index is not None else "--")
d2.metric("strict index", f"{row.strict_index:.2f}" if row.strict_index is not None else "--")

if row.outcomes:
    st.write("outcomes:", row.outcomes)

pat = next((p for p in corpus.patterns if p.id == choice), None)
if pat is not None:
    statement = pat.front_matter.get("canonical_statement")
    if statement:
        st.markdown(f"**canonical statement.** {statement}")

cases = [c for c in corpus.cases if c.pattern_id == choice]
if cases:
    st.markdown("**application cases**")
    for c in cases:
        outcome = c.front_matter.get("outcome") or "still-pending"
        domain = c.front_matter.get("domain", "?")
        opened = c.front_matter.get("opened_at", "?")
        st.markdown(
            f"- `{c.id}` ({domain}, opened {opened}) — **{outcome}**"
        )
else:
    st.caption("no application cases recorded for this pattern yet.")

# ---------------------------------------------------------------------------
# interactive: validate your own case against the real schema engine
# ---------------------------------------------------------------------------
st.divider()
st.subheader("validate a case yourself")
st.caption(
    "the table above is read-only. this section drives the real validator "
    "(`procurement_pattern_library.validator.validate`): paste a case with "
    "yaml front-matter, pick the as-of date, and the same schema + ninety-day "
    "outcome rules that gate the committed corpus run live on your input."
)

EXAMPLE_CASE = """---
id: my-new-case
pattern_id: dual-source
domain: ai-build
upstream_artifact: repo://my-repo/decisions/DEC-001.md
opened_at: 2026-05-01
outcome: transferred-with-friction
---

# My case

Free-text body describing how the pattern applied. The validator
only enforces the front-matter; this prose is not scored.
"""

pattern_ids = sorted(p.id for p in corpus.patterns if p.id)

ic1, ic2 = st.columns([3, 1])
with ic2:
    as_of = st.date_input(
        "as-of date (drives the ninety-day rule)",
        value=date(2026, 6, 22),
    )
    st.caption(
        "a case opened more than 90 days before this date with an empty "
        "`outcome` is an error — that is the rule the validator enforces."
    )
    st.markdown("**known pattern ids**")
    st.write(pattern_ids or "(none)")

with ic1:
    case_text = st.text_area(
        "case markdown (yaml front-matter + body)",
        value=EXAMPLE_CASE,
        height=320,
    )

if st.button("validate", type="primary"):
    try:
        fm, body = parse_front_matter(case_text)
    except LoaderError as exc:
        st.error(f"could not parse front-matter: {exc}")
    else:
        # build a one-case corpus that reuses the real committed patterns so
        # pattern_id cross-checks resolve. the validator treats the declared
        # pattern_id as the directory id, so we mirror it here.
        declared_pid = str(fm.get("pattern_id", ""))
        probe = Case(
            front_matter=fm,
            body=body,
            path=Path(f"{fm.get('id', 'pasted')}.md"),
            directory_pattern_id=declared_pid,
        )
        probe_corpus = Corpus(
            patterns=corpus.patterns,
            cases=[probe],
            root=ROOT,
        )
        result = validate(probe_corpus, today=as_of)

        # only surface issues raised against the pasted case, not the
        # committed patterns (which validate cleanly already).
        case_errors = [i for i in result.errors if i.path == probe.path]
        case_warnings = [i for i in result.warnings if i.path == probe.path]

        if not case_errors:
            st.success("PASS — this case satisfies the schema and the ninety-day rule.")
        else:
            st.error(
                f"FAIL — {len(case_errors)} error(s). this case would be "
                f"rejected by `validate`."
            )
            for issue in case_errors:
                st.markdown(f"- **error** — {issue.message}")

        if case_warnings:
            st.markdown("**warnings**")
            for issue in case_warnings:
                st.markdown(f"- {issue.message}")

        with st.expander("parsed front-matter (what the validator saw)"):
            st.json(fm)
