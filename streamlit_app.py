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

from procurement_pattern_library.loader import load_corpus
from procurement_pattern_library.score import ScoreWeights
from procurement_pattern_library.show import summarize

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
