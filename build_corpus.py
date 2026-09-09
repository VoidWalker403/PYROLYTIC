"""
PyroLytic RAG — Step 1: Build the corpus manifest.

Rather than a separate, disconnected "pile of papers," this corpus is
deliberately built FROM the same 26 sources already cited in
pyrolysis_yields.csv. This keeps the RAG layer and the yield dataset
traceable to the same evidence base - when the LLM cites a source, it's
one that also contributed real data rows, not an arbitrary document.

This script produces corpus_manifest.csv - a list of unique papers with
their DOI/URL and the data rows they support. Actual PDF/text ingestion
(ingest.py) is a separate step, since it requires downloading each paper,
which needs to run wherever real internet + storage exists (i.e. your
machine, not this sandbox).
"""
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
df = pd.read_csv(PROJECT_DIR / 'pyrolysis_yields.csv')

manifest = (df.groupby(['source_title', 'source_doi'])
            .agg(n_data_rows=('plastic_type', 'count'),
                 plastic_types=('plastic_type', lambda x: ','.join(sorted(set(x)))),
                 avg_confidence=('confidence', 'mean'))
            .reset_index()
            .sort_values('n_data_rows', ascending=False))

manifest.to_csv(PROJECT_DIR / 'corpus_manifest.csv', index=False)
print(f"Corpus manifest: {len(manifest)} unique papers")
print(manifest.to_string(index=False))
