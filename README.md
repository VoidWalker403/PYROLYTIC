# PyroLytic

A Streamlit research prototype for exploring waste-plastic pyrolysis literature,
with local authentication, ChromaDB retrieval, a local Ollama chatbot, and a
simplified comparison of downstream processing routes.

## Run locally

Use Python 3.10 or newer. From this repository's directory:

```sh
python -m venv .venv
# Activate .venv using the command for your shell.
python -m pip install -r requirements.txt
python auth.py
```

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace
the placeholder with your generated password hash. See [AUTHENTICATION.md](AUTHENTICATION.md)
for account setup and session behavior. Then run:

```sh
streamlit run app.py
```

Demo mode uses prerecorded responses and does not need Ollama or a vector index.
For live retrieval, install and start Ollama, then run:

```sh
ollama pull qwen2.5:7b
python ingest.py
streamlit run app.py
```

Ingestion downloads the sentence-transformer model on first use. Disable Demo
Mode in the sidebar to query the local pipeline.

## Included files

- `pyrolysis_yields.csv`: extracted literature data with source identifiers and confidence notes.
- `build_corpus.py`: rebuilds `corpus_manifest.csv` from the dataset.
- `ingest.py`, `retrieve.py`, `explain.py`: embedding, retrieval, and explanation pipeline.
- `route_comparison.py`: simplified economics and sensitivity calculations.
- `eda.ipynb`: exploratory analysis; launch Jupyter from the repository directory.
- `tests/`: authentication and Streamlit interface tests (`python -m pytest`).

## Current limitations

Some demo responses reference model training results, `models/model_card.md`, and
`economics/economics_card.md`. Those training scripts and reports are not included
in this repository, so their reported model scores cannot be reproduced here.
Demo responses are static examples, not fresh calculations. LLM grounding is
prompt-based and does not guarantee factual answers. Literature values and
economic assumptions require independent validation for practical use.

## Files kept local

Git ignores real Streamlit secrets, environment files, private keys, virtual
environments, caches, the generated ChromaDB store, and additional files placed
in `raw_texts/`. Only the project-authored background note is included from that
directory. Do not put credentials or private material in source code, CSVs, or
notebook cells; clear notebook outputs before committing.
