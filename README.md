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
- `research_library.py`: searchable paper catalog, local review workflow and filtered CSV export.
- `research_library.json`: public bibliographic discovery snapshot with DOI and metadata provenance.
- `discover_papers.py`: repeatable Crossref discovery; refreshes metadata without inventing experiments.
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

The repository does not include a trained yield predictor or reproducible model
evaluation reports. Demo responses are labeled static workflow examples and make
no model-accuracy or calculated route-ranking claims. LLM grounding is
prompt-based and does not guarantee factual answers. Literature values and
economic assumptions require independent validation for practical use.

## Free deployment options

### Online preview

[Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud) offers free hosting for Streamlit apps connected to GitHub. Select this repository, its intended branch, and `app.py`; add the `[auth.users]` configuration in the host's Secrets settings rather than uploading `.streamlit/secrets.toml`. Only committed and pushed files are deployed.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the exact Community Cloud configuration,
secret template, sharing model, and post-launch checks.

The app starts in Demo Mode, which shows static example answers—not live AI. On startup it can rebuild its SQLite database from the tracked CSV and load `research_library.json` if that snapshot is included in the deployed branch. Changes to notes, curation, imports, and provenance are written to local SQLite. Community Cloud does not guarantee local-file persistence, so do not use its filesystem as the permanent store for edits. Use an external database and adapt the app before relying on shared, persistent changes.

Community Cloud apps sleep after 12 hours without traffic. Its published resource limits are approximate (about 0.69–2.7 GB RAM) and may change. This project's runtime requirements include scientific packages, ChromaDB, and sentence-transformers; the full app may exceed a small instance's resources. Remove development-only packages from the hosted requirements and test a deployment before sharing it.

### Live Ollama answers

`explain.py` currently calls a local Ollama server with `qwen2.5:7b`. A hosted app cannot access the `E:\` USB drive or Ollama at `localhost` on your laptop. To keep this exact local setup, both Streamlit and Ollama must run on the same computer, which must stay on and connected; do not expose Ollama's unauthenticated local API directly to the public internet.

For a cloud-hosted live chatbot, add a server-side client/configuration for [Ollama's cloud API](https://docs.ollama.com/cloud), store its API key in the host's Secrets, and choose a model actually listed by that API. The current `ollama.chat()` call defaults to local Ollama, so this cloud connection is not configured yet. Ollama's [free plan](https://ollama.com/blog/transparent-pricing) includes only a small monthly allowance for starter models; it is not unlimited free inference. Prompts sent to the cloud are processed by Ollama, so only use this option for data you are comfortable sending there.

## Research library and curation

The September 25, 2026 snapshot contains **582 unique Crossref DOI records**.
Combined with the existing dataset it produces **607 library records**, including
**580 additional papers awaiting extraction**. The **146 existing experiments**
and their annotations are preserved. Counts describe this snapshot and can change
with later local imports. A library paper is a bibliographic record, not a
downloaded PDF, a verified yield, or proof of scientific quality.

After login, use **Research paper library** to search titles/authors/DOIs/journals,
filter by publication year, topic, review status, article type, or extraction
coverage, and open the publisher's DOI page. Results are paginated in groups of
50. Select a paper on the current page to save **Unreviewed**, **Shortlisted**,
**Reviewed**, or **Excluded** status and local notes. Reviewed means you reviewed
the record; it does not certify its measurements. Conflicting edits from another
session are rejected; use **Reload saved review** to obtain its current values.
Export applies to all filtered results, including those on other pages.

The catalog adds tables to the existing SQLite database and never changes paper
or experiment records. Equivalent bare DOI and doi.org identifiers are merged
within the catalog. Refreshes retain notes, review status and omitted papers.
The bundled snapshot loads locally after authentication; opening the app does not
call Crossref. New experiment sources are added to the catalog on the next rerun.

To refresh from the public API, from the project directory:

```sh
python discover_papers.py --rows 100 --until 2026-09-25 --import-library
```

Omit `--until` to use today's date. `--rows` is the result limit **per query**
(1–1000), not a guaranteed number of new papers. Eight topic searches cover
plastic waste, polyethylene, polypropylene, catalysis, polystyrene, mixtures,
kinetics and sustainability/economics. The saved snapshot records the queries,
retrieval time and per-paper metadata URLs. Searches use title relevance, not a
systematic-review protocol. Titles must mention pyrolysis and plastics/a listed
polymer; obvious correction/retraction notices and a news publication are filtered.
This is not a comprehensive retraction or quality check. Article/review and topic
labels are heuristic. Crossref metadata can be incomplete or inaccurate.

Failed requests have bounded retries and timeouts. The snapshot is replaced only
after all queries succeed. There are no new package dependencies or API-key
requirements. Metadata is provided by the
[Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/).

New library metadata is deliberately separate from the evidence index: live chat
continues to retrieve extracted experiments and local text. To add quantitative
evidence, obtain permitted access to a paper, verify measurements/units and
page/table provenance, use **Import experiments**, and rebuild the search index.
Do not treat a metadata-only library expansion as added experimental evidence.

The temperature filter supports missing, constant and decimal temperatures.
Live-chat failures display recovery guidance without exposing exception details;
only the exception class is logged locally.

## Files kept local

Git ignores real Streamlit secrets, environment files, private keys, virtual
environments, caches, the generated ChromaDB store, and additional files placed
in `raw_texts/`. Only the project-authored background note is included from that
directory. Do not put credentials or private material in source code, CSVs, or
notebook cells; clear notebook outputs before committing.
