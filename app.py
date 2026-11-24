"""Authenticated research library, experiment curation and local retrieval dashboard."""
import streamlit as st
import logging
import sys
import time
from pathlib import Path
from auth import require_login
from literature_browser import render as render_literature_browser
from literature_browser import query_experiments
from analytics import render as render_analytics

sys.path.insert(0, str(Path(__file__).parent / 'rag'))
sys.path.insert(0, str(Path(__file__).parent / 'llm'))

st.set_page_config(page_title="PyroLytic", page_icon="\U0001F525", layout="wide")

require_login()

from chat_sources import capture_sources, render_answer
from research_library import ensure_library, query_library, render as render_research_library

ensure_library()
library_count = len(query_library())

experiment_rows = query_experiments()
experiment_count = len(experiment_rows)
paper_count = len({row["doi"] for row in experiment_rows})
confidence_values = [row["confidence"] for row in experiment_rows if row["confidence"] is not None]
average_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
pp_count = sum(row["plastic_type"] == "PP" for row in experiment_rows)

# Static examples explain the workflow; no unavailable model scores are claimed.
DEMO_QA = [
    {
        "question": "What oil yield can I expect from PP pyrolysis at around 500°C?",
        "answer": (
            "This is a static example, not a yield prediction. Filter the literature browser "
            "to PP and the temperature range you need, then check catalyst, reactor, feedstock "
            "and source provenance. Measurements from different studies should not be treated "
            "as interchangeable. The research library provides additional papers to review; "
            "their metadata does not establish an experimental yield."
        ),
    },
    {
        "question": "Why is Route B (petrochemical) ranked higher than Route A (fuel oil)?",
        "answer": (
            "This static example does not establish a route ranking. The included route "
            "comparison is a simplified scenario calculator. Review capital costs, product "
            "prices, operating costs and sensitivity assumptions before comparing results. "
            "A larger paper library helps locate relevant evidence but does not validate "
            "the project's economic assumptions."
        ),
    },
    {
        "question": "How reliable is the yield prediction model?",
        "answer": (
            "This repository does not include a trained yield predictor or the training "
            "reports needed to reproduce a predictive score. No accuracy claim is made here. "
            "Use Data quality to screen the existing experiments, review their sources, "
            "and validate any future model using held-out papers to reduce leakage."
        ),
    },
]

# ---- Sidebar: project stats ----
with st.sidebar:
    st.title("PyroLytic")
    st.caption("AI-Assisted Waste Plastic Pyrolysis Process Advisor")
    st.divider()
    st.metric("Experiment rows", f"{experiment_count:,}")
    st.metric("Unique source papers", f"{paper_count:,}")
    st.caption(f"Research library: {library_count:,} records, including papers awaiting extraction.")
    st.metric("Average extraction confidence", f"{average_confidence:.2f}")
    st.metric("PP experiment rows", f"{pp_count:,}")
    st.divider()
    demo_mode = st.toggle("Demo Mode (static examples)", value=True,
                         help="ON shows static workflow examples. OFF queries the local model and experiment index.")
    st.caption("Live mode requires a current search index and a running local Ollama model.")

# ---- Main chat interface ----
st.header("Ask PyroLytic")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg['role'] == 'assistant':
            render_answer(msg)
        else:
            st.markdown(msg["content"])

if demo_mode:
    st.info("Demo Mode is ON — try one of the static example questions below, or type your own "
            "to see the closest match.", icon="\u2139\ufe0f")
    cols = st.columns(len(DEMO_QA))
    for i, (col, qa) in enumerate(zip(cols, DEMO_QA)):
        if col.button(qa["question"], key=f"demo_{i}"):
            st.session_state.messages.append({"role": "user", "content": qa["question"]})
            st.session_state.messages.append({"role": "assistant", "content": qa["answer"]})
            st.rerun()

if prompt := st.chat_input("Ask about pyrolysis conditions, routes, or model reliability..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer_sources = None
        if demo_mode:
            # Closest static example by simple keyword overlap - avoids
            # calling the live model in demo mode, keeps latency at zero
            best_match = max(DEMO_QA, key=lambda qa: len(
                set(prompt.lower().split()) & set(qa["question"].lower().split())))
            response = (f"*(Demo Mode - closest static example shown)*\n\n{best_match['answer']}")
            st.markdown(response)
        else:
            with st.spinner("Querying local model (10-25s expected on CPU)..."):
                try:
                    from retrieve import retrieve
                    from explain import explain
                    start = time.time()
                    retrieved = retrieve(prompt, k=3)
                    captured = capture_sources(retrieved)
                    response = explain(prompt, retrieved_chunks=retrieved, verbose_timing=False)
                    answer_sources = captured
                    elapsed = time.time() - start
                    render_answer({'content': response, 'sources': answer_sources})
                    st.caption(f"Live response in {elapsed:.1f}s")
                except Exception as error:
                    # Log the failure category without query text, source text or secrets.
                    logging.getLogger(__name__).warning("Live pipeline failed (%s)", type(error).__name__)
                    response = ("Live answers are unavailable. Check the search-index status below "
                                "and confirm that Ollama and the configured model are running locally.")
                    st.error(response)

        message = {"role": "assistant", "content": response}
        if answer_sources is not None:
            message['sources'] = answer_sources
        st.session_state.messages.append(message)

st.divider()
render_research_library()

st.divider()
render_literature_browser()

from paper_details import render as render_paper_details
st.divider()
render_paper_details()

st.divider()
render_analytics()

from import_preview import render as render_import_preview
st.divider()
render_import_preview()

from search_index import render as render_search_index
st.divider()
render_search_index()

from data_quality import render as render_data_quality
st.divider()
render_data_quality()
