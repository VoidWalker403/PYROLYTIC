"""
PyroLytic — Streamlit Chatbot Dashboard (Week 9)

RUN ON YOUR OWN MACHINE: streamlit run app.py
Requires: Week 0 (Ollama), Week 7 (RAG index built), Week 8 (llm/explain.py) all working.

DEMO SAFETY NET: includes a "Demo Mode" toggle using pre-verified real answers
(built from actual project data, not fabricated) in case live model latency
or an unexpected error happens during a live presentation. Live Mode calls
the real pipeline; Demo Mode replays known-good, pre-tested exchanges.
Always test Live Mode yourself before presenting - don't rely on Demo Mode
as your only rehearsal.
"""
import streamlit as st
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

experiment_rows = query_experiments()
experiment_count = len(experiment_rows)
paper_count = len({row["doi"] for row in experiment_rows})
confidence_values = [row["confidence"] for row in experiment_rows if row["confidence"] is not None]
average_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
pp_count = sum(row["plastic_type"] == "PP" for row in experiment_rows)

# ---- Pre-verified demo exchanges (real project data, not invented) ----
DEMO_QA = [
    {
        "question": "What oil yield can I expect from PP pyrolysis at around 500°C?",
        "answer": (
            "Based on the retrieved literature, PP pyrolysis oil yield at 500°C varies "
            "considerably depending on catalyst use: **[SOURCE: 10.1038/s41598-023-37769-8]** "
            "reports 70.0% oil yield with no catalyst, rising to 80.8% with a kaolin catalyst "
            "at a 1:2 ratio. However, **[SOURCE: 10.3390/polym16101302]** reports a much lower "
            "41.9% oil yield at the same temperature under different reactor conditions "
            "(fixed-bed, varying feedstock mass).\n\n"
            "This spread is exactly why the project's narrow-scope model (n=16, R²=0.57) only "
            "achieves moderate predictive power even within a single study — reactor design "
            "and feedstock loading matter as much as temperature alone."
        ),
    },
    {
        "question": "Why is Route B (petrochemical) ranked higher than Route A (fuel oil)?",
        "answer": (
            "Route B (petrochemical feedstock / BTX) has a substantially higher NPV ($77.9m vs "
            "$17.0m) and IRR (44.6% vs 19.7%) than Route A at the base case. More importantly, "
            "sensitivity analysis shows Route A is fragile: a 20% drop in product price nearly "
            "eliminates its entire NPV (down to $0.6m), while Route B stays strongly profitable "
            "under the same shock ($46.1m). Route B costs more to build (higher CAPEX for "
            "catalytic upgrading equipment) but is structurally less risky, not just more "
            "profitable — see `economics/economics_card.md` for full sensitivity tables."
        ),
    },
    {
        "question": "How reliable is the yield prediction model?",
        "answer": (
            "It depends on scope, and this project reports both results honestly. On PP data "
            "from a single clean study (16 rows, one reactor, a real 3-factor experimental "
            "design), a quadratic model explains 57% of oil-yield variance under leave-one-out "
            "cross-validation — a genuine result.\n\n"
            "On the full 146-row literature-aggregated dataset, the model reaches R²≈0.23, but "
            "a stratified check revealed why: within any single plastic type except PP, the "
            "model has essentially no predictive power beyond guessing that type's average "
            "yield. The overall R² is mostly the model learning to distinguish *which plastic "
            "type* a row is, not how conditions drive yield within a type. PP is the exception "
            "because it has the most densely-sampled conditions — which is also why it's the "
            "only type with a strong narrow-scope result. See `models/model_card.md` Section 6 "
            "for the full diagnostic."
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
    st.metric("Average extraction confidence", f"{average_confidence:.2f}")
    st.metric("PP experiment rows", f"{pp_count:,}")
    st.divider()
    demo_mode = st.toggle("Demo Mode (pre-verified answers)", value=True,
                           help="ON = safe, pre-tested answers for live presentation. "
                                "OFF = calls the real local LLM + RAG pipeline (10-25s latency).")
    st.caption("Turn OFF to show the live pipeline is real, not just a scripted demo — "
               "but test this yourself beforehand.")

# ---- Main chat interface ----
st.header("Ask PyroLytic")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if demo_mode:
    st.info("Demo Mode is ON — try one of the pre-verified questions below, or type your own "
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
        if demo_mode:
            # Closest pre-verified match by simple keyword overlap - avoids
            # calling the live model in demo mode, keeps latency at zero
            best_match = max(DEMO_QA, key=lambda qa: len(
                set(prompt.lower().split()) & set(qa["question"].lower().split())))
            response = (f"*(Demo Mode - closest pre-verified match shown)*\n\n{best_match['answer']}")
            st.markdown(response)
        else:
            with st.spinner("Querying local model (10-25s expected on CPU)..."):
                try:
                    from retrieve import retrieve
                    from explain import explain
                    start = time.time()
                    retrieved = retrieve(prompt, k=3)
                    response = explain(prompt, retrieved_chunks=retrieved, verbose_timing=False)
                    elapsed = time.time() - start
                    st.markdown(response)
                    st.caption(f"Live response in {elapsed:.1f}s")
                except Exception as e:
                    response = (f"Live pipeline error: {e}\n\nThis is why Demo Mode exists as a "
                                f"presentation safety net — switch it on in the sidebar.")
                    st.error(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

st.divider()
render_literature_browser()

st.divider()
render_analytics()
