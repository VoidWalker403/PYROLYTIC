"""
PyroLytic LLM Explanation Layer — Week 8

RUN THIS ON YOUR OWN MACHINE (needs Ollama running locally with qwen2.5:7b
or qwen2.5:7b-instruct-q4_K_M pulled - see Week 0 setup).

Core grounding principle (stated throughout this project): the LLM explains
and cites, it NEVER calculates or invents a number the pipeline didn't
produce. This is enforced structurally here, not just requested in the
prompt - see build_prompt() for how model outputs and retrieved sources are
kept separate from the LLM's own generated text.
"""
import ollama
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'rag'))

MODEL_NAME = 'qwen2.5:7b'  # switch to 'qwen2.5:7b-instruct-q4_K_M' on lower-RAM machines
# IMPORTANT: no '-cloud' suffix - this must run locally, per the project's
# privacy/always-on requirements established in Week 0. Verify with
# `ollama ps` that PROCESSOR shows local CPU, not a forwarded cloud call.

SYSTEM_PROMPT = """You are an assistant embedded in PyroLytic, a plastic pyrolysis process \
advisor. You have two kinds of information available to you in each prompt:

1. PIPELINE OUTPUTS - numbers already calculated by the yield model or economics module. \
These are ground truth for this conversation. Repeat them exactly; never recalculate, \
round differently, or "improve" them.

2. RETRIEVED SOURCES - excerpts from published papers, each tagged [SOURCE: doi_or_url]. \
When you reference information from these, cite the source tag. If no retrieved source \
supports a claim you want to make, do not make that claim - say the information isn't \
available in the current corpus instead of filling the gap from general knowledge.

Never state a numeric yield, cost, or economic figure that does not appear verbatim in \
the PIPELINE OUTPUTS or RETRIEVED SOURCES sections. If asked something outside both, say \
so plainly rather than guessing.
"""


def build_prompt(user_question, pipeline_outputs=None, retrieved_chunks=None):
    """
    Assembles a grounded prompt. pipeline_outputs is a dict of already-
    calculated values (e.g. from models/train.py or economics/route_comparison.py).
    retrieved_chunks is the output of rag.retrieve.retrieve() - kept as a
    separate, clearly-labeled section so the LLM can distinguish "what the
    pipeline computed" from "what the literature says" from "the question".
    """
    sections = []

    if pipeline_outputs:
        lines = ["=== PIPELINE OUTPUTS (ground truth - repeat exactly, do not recalculate) ==="]
        for k, v in pipeline_outputs.items():
            lines.append(f"{k}: {v}")
        sections.append("\n".join(lines))

    if retrieved_chunks:
        lines = ["=== RETRIEVED SOURCES (cite using [SOURCE: doi] when referenced) ==="]
        for chunk in retrieved_chunks:
            lines.append(f"[SOURCE: {chunk['source_doi']}]\n{chunk['text']}\n")
        sections.append("\n".join(lines))

    sections.append(f"=== QUESTION ===\n{user_question}")

    return "\n\n".join(sections)


def explain(user_question, pipeline_outputs=None, retrieved_chunks=None, verbose_timing=True):
    """
    Full pipeline: build grounded prompt, call local Ollama, return response.
    Set verbose_timing=True to print latency - useful for demo prep, since
    expect ~10-25s on CPU for a 20B model (established in Week 0 baseline).
    """
    import time
    prompt = build_prompt(user_question, pipeline_outputs, retrieved_chunks)

    start = time.time()
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt},
        ]
    )
    elapsed = time.time() - start

    if verbose_timing:
        print(f"[latency: {elapsed:.1f}s, model: {MODEL_NAME}]")

    return response['message']['content']


if __name__ == '__main__':
    # Example: explain a route ranking decision, grounded in the Week 5-6
    # economics output and Week 7 retrieved literature.
    from retrieve import retrieve, format_for_llm_context

    pipeline_outputs = {
        'Route A (fuel oil) NPV': '$17.0m',
        'Route B (petrochemical/BTX) NPV': '$77.9m',
        'Route A IRR': '19.7%',
        'Route B IRR': '44.6%',
        'Route A sensitivity to -20% product price': 'NPV drops to $0.6m (near breakeven)',
        'Route B sensitivity to -20% product price': 'NPV drops to $46.1m (stays strongly profitable)',
    }

    retrieved = retrieve("PP pyrolysis oil yield temperature effects", k=5)

    question = "Why is Route B ranked higher than Route A, and what does the literature say about achievable oil yields that this ranking depends on?"

    print(explain(question, pipeline_outputs=pipeline_outputs, retrieved_chunks=retrieved))
