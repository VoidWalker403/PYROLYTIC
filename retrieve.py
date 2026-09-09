"""
PyroLytic RAG — Step 3: Retrieval.

RUN THIS ON YOUR OWN MACHINE after running ingest.py there first.

Provides retrieve(query, k) -> list of (text, metadata, distance) for use
by the LLM explanation layer (Week 8). Citation tracking is built in via
metadata - every retrieved chunk carries its source_doi, so the LLM layer
can cite it rather than inventing a source.
"""
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

CHROMA_DIR = Path(__file__).parent / 'chroma_db'
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

_model = None
_collection = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection('pyrolytic_corpus')
    return _collection

def retrieve(query, k=5):
    """
    Returns top-k chunks relevant to query, each with source metadata
    for citation. Distance is cosine distance - lower is more similar.
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)

    out = []
    for i in range(len(results['ids'][0])):
        out.append({
            'text': results['documents'][0][i],
            'source_doi': results['metadatas'][0][i].get('source_doi'),
            'source_title': results['metadatas'][0][i].get('source_title', ''),
            'chunk_type': results['metadatas'][0][i].get('chunk_type'),
            'distance': results['distances'][0][i],
        })
    return out

def format_for_llm_context(results):
    """
    Formats retrieved chunks into a citation-ready block for the LLM
    prompt (Week 8) - each chunk is tagged with a [SOURCE: doi] marker
    so the LLM can cite it directly rather than paraphrasing without
    attribution.
    """
    blocks = []
    for r in results:
        blocks.append(f"[SOURCE: {r['source_doi']}]\n{r['text']}\n")
    return "\n---\n".join(blocks)

if __name__ == '__main__':
    # Quick manual test - run after ingest.py has populated the index
    test_queries = [
        "What oil yield can I expect from PP pyrolysis at 500C?",
        "How does catalyst choice affect HDPE pyrolysis yield?",
        "What is the effect of residence time on LDPE oil yield?",
    ]
    for q in test_queries:
        print(f"\n=== Query: {q} ===")
        results = retrieve(q, k=3)
        for r in results:
            print(f"  [{r['chunk_type']}] {r['source_title'][:60]} (distance={r['distance']:.3f})")
