"""
PyroLytic RAG — Step 2: Ingest corpus into ChromaDB.

RUN THIS ON YOUR OWN MACHINE, not in a sandbox - it needs real internet
access (to fetch papers) and writes a persistent ChromaDB store to disk.

Two-tier approach given the corpus is small (16 unique documents):
1. For each document, store what we ALREADY know about it from the yield
   dataset (source title, DOI, which conditions/results it reported) as
   a baseline "abstract-level" chunk - this works even before you've
   downloaded any PDFs.
2. Optionally, drop full paper text/PDFs into rag/raw_texts/<doi_safe>.txt
   and this script will chunk and embed those too, giving much richer
   retrieval than the dataset-derived summaries alone.

This means the RAG layer is useful from day one (grounded in exactly what
we've already extracted) and improves incrementally as you add full texts.
"""
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import re

DATA_PATH = Path(__file__).resolve().parent / 'pyrolysis_yields.csv'
RAW_TEXTS_DIR = Path(__file__).parent / 'raw_texts'
CHROMA_DIR = Path(__file__).parent / 'chroma_db'

EMBEDDING_MODEL = 'all-MiniLM-L6-v2'  # small, fast, CPU-friendly - good fit given no GPU

def safe_filename(doi_or_url):
    return re.sub(r'[^a-zA-Z0-9]', '_', doi_or_url)[:100]

def build_dataset_summary_chunks(df):
    """
    Tier 1: one chunk per unique source document, summarizing what we
    extracted from it. Always available, no download required.
    """
    chunks = []
    for doi, group in df.groupby('source_doi'):
        title = group['source_title'].iloc[0]
        plastic_types = ', '.join(sorted(group['plastic_type'].unique()))
        n_rows = len(group)
        temp_range = f"{group['temperature_C'].min():.0f}-{group['temperature_C'].max():.0f}C"
        avg_conf = group['confidence'].mean()
        conditions_summary = []
        for _, row in group.iterrows():
            cond = f"{row['plastic_type']} at {row['temperature_C']:.0f}C"
            if pd.notna(row['catalyst']) and row['catalyst'] != 'none':
                cond += f" with {row['catalyst']} catalyst"
            cond += f": oil={row['oil_yield_wt%']:.1f}%"
            if pd.notna(row['gas_yield_wt%']):
                cond += f", gas={row['gas_yield_wt%']:.1f}%"
            if pd.notna(row['char_yield_wt%']):
                cond += f", char={row['char_yield_wt%']:.1f}%"
            conditions_summary.append(cond)

        text = (f"Source: {title}\n"
                f"DOI/URL: {doi}\n"
                f"Plastic types studied: {plastic_types}\n"
                f"Temperature range: {temp_range}\n"
                f"Data confidence: {avg_conf:.1f} (1.0=primary/exact, 0.6=secondary/approximate, 0.3=flagged issue)\n"
                f"Extracted conditions and yields:\n" + "\n".join(f"  - {c}" for c in conditions_summary))

        chunks.append({
            'id': f"summary_{safe_filename(doi)}",
            'text': text,
            'metadata': {'source_doi': doi, 'source_title': title, 'chunk_type': 'dataset_summary'}
        })
    return chunks

def build_fulltext_chunks(chunk_size=500, overlap=50):
    """
    Tier 2: chunk any full-text files found in raw_texts/. Simple
    word-based chunking - adequate for a corpus this size; swap for a
    proper sentence-aware chunker if retrieval quality needs improving.
    """
    chunks = []
    if not RAW_TEXTS_DIR.exists():
        return chunks
    for txt_file in RAW_TEXTS_DIR.glob('*.txt'):
        text = txt_file.read_text(encoding='utf-8', errors='ignore')
        words = text.split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            if len(chunk_words) < 20:
                continue
            chunks.append({
                'id': f"fulltext_{txt_file.stem}_{i}",
                'text': ' '.join(chunk_words),
                'metadata': {'source_doi': txt_file.stem, 'chunk_type': 'fulltext'}
            })
    return chunks

def main():
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    print("Building Tier 1 chunks (dataset-derived summaries, always available)...")
    summary_chunks = build_dataset_summary_chunks(df)
    print(f"  {len(summary_chunks)} document summaries built")

    print("Building Tier 2 chunks (full text, if any files present in rag/raw_texts/)...")
    fulltext_chunks = build_fulltext_chunks()
    print(f"  {len(fulltext_chunks)} full-text chunks found")
    if not fulltext_chunks:
        print(f"  (No files in {RAW_TEXTS_DIR} yet - drop .txt files there to enrich retrieval)")

    all_chunks = summary_chunks + fulltext_chunks

    print(f"\nLoading embedding model ({EMBEDDING_MODEL})...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Embedding and storing in ChromaDB...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection('pyrolytic_corpus')

    texts = [c['text'] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    collection.upsert(
        ids=[c['id'] for c in all_chunks],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[c['metadata'] for c in all_chunks],
    )

    print(f"\nDone. {len(all_chunks)} chunks stored in {CHROMA_DIR}")
    print(f"Run retrieve.py to test queries against this index.")

if __name__ == '__main__':
    main()
