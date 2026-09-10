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
- `database.py`: imports the CSV into a local SQLite database with paper and experiment provenance.
- `literature_browser.py`: provides the filterable Streamlit literature browser and provenance inspector.
- `analytics.py`: renders yield and confidence charts from the SQLite records.
- `paper_details.py`: source links, full experiment records, and editable page/table/extraction provenance after login.
- `import_preview.py`: review a CSV upload before explicitly saving it to the local database.
- `chat_sources.py`: clickable live-answer citations, retrieved excerpts, and captured experiment details.
- `data_quality.py`: read-only screening findings with source links and experiment navigation.
- Sidebar metrics are calculated from SQLite at runtime so they stay synchronized with imported data.
- `ingest.py`, `retrieve.py`, `explain.py`: embedding, retrieval, and explanation pipeline.
- `route_comparison.py`: simplified economics and sensitivity calculations.
- `eda.ipynb`: exploratory analysis; launch Jupyter from the repository directory.
- `tests/`: authentication and Streamlit interface tests (`python -m pytest`).

To create or refresh the local database, run `python database.py`. This creates
`pyrolytic.sqlite3`, which is ignored by Git.

Use **Paper details** after signing in to select a paper and annotate an experiment.
Annotations are stored only in the local database, not in the CSV or public repository.
Back up the database to preserve them. Imports match experiments by DOI and normalized
imported content, including run notes, rather than CSV row positions. Reordering or
inserting rows preserves existing IDs and annotations. Numeric formatting differences
such as `500` and `500.0` do not create new records.

Omitted experiments are retained with a blank current CSV row; they still appear in
the browser and dataset metrics. Correcting measurements, confidence, or notes creates
a new record without transferring annotations from the old record. Review the retained
record before using the combined dataset. Imports treat each CSV as a complete snapshot
for current row positions. Indistinguishable duplicate rows are rejected: distinguish
real replicate runs in their notes. Invalid input is rejected before records are changed.
Existing databases gain content identities on the next import without changing record IDs.
Concurrent changes to provenance are rejected; reload the page before retrying.

Use **Import experiments** after signing in to upload a UTF-8 CSV (up to 5 MB).
The preview shows new, matching, and retained experiments plus paper title changes,
without writing to the database. Review the tables, acknowledge the changes, then
select **Save import to local database**. If another session changes the data, refresh
the preview and review it again. Invalid or empty CSVs cannot be saved.
Importing does not modify the tracked CSV or automatically rebuild ChromaDB.
Use **Rebuild search index** after saving an upload or editing provenance (or run
`python ingest.py`). Indexing reads SQLite, including retained experiments, and optional
`raw_texts/*.txt` files. It only imports the tracked CSV if no database exists.

Live retrieval rejects missing or outdated indexes. Each rebuild creates a separate
collection and selects it only after all chunks are written and the sources are checked
again. Failed rebuilds leave the previous selection intact; stale data cannot be queried.
Old collections remain locally for now and consume disk space. The first rebuild downloads
the embedding model; documents are embedded locally. Rebuilds do not install or start
Ollama, which is still needed for live generated answers.

Live answers keep their retrieved sources and experiment details in the browser session.
Matching `[SOURCE: ...]` markers become clickable links when a valid DOI or web URL is
available. Expand a source to inspect its excerpts, yields, conditions, and provenance.
Sources cited by the answer are labeled separately from other retrieved context; unknown
source markers trigger a warning. This checks source membership, not scientific correctness.
Saved chat details remain as captured even after database edits, and logout clears them.

**Data quality** flags missing core fields and page/table provenance, invalid numeric
ranges, incomplete yields, and complete yield totals more than 5 percentage points
from 100%. It also screens composition totals, retained records, wax-to-oil mappings
noted in the data, and temperatures outside a heuristic 100–1200 °C band. Missing
measurements are never treated as zero. These are review prompts, not corrections or
claims that the underlying paper is wrong. Original units are not stored separately;
the report states expected column units but cannot verify unit conversions automatically.
Filter by severity/check and use **Show experiment in Paper details** to inspect the record.

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
