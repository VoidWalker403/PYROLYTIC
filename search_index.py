"""Versioned search snapshots of SQLite experiments and optional local texts."""

from contextlib import closing
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import uuid

import database

CHROMA_DIR = database.PROJECT_DIR / "chroma_db"
RAW_TEXTS_DIR = database.PROJECT_DIR / "raw_texts"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
FORMAT_VERSION = 1


def _parts(text):
    words = text.split()
    for start in range(0, len(words), 80):
        yield " ".join(words[start:start + 100])


def snapshot(database_path=database.DEFAULT_DATABASE, raw_texts_dir=RAW_TEXTS_DIR):
    """Read a consistent database snapshot without importing CSV or writing data."""
    uri = Path(database_path).resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute("BEGIN")
        papers = {row["id"]: dict(row) for row in connection.execute("SELECT * FROM papers")}
        records = [dict(row) for row in connection.execute("SELECT * FROM experiments ORDER BY id")]
    chunks = []
    for row in records:
        paper = papers[row["paper_id"]]
        labels = [(column, row[column]) for _, column, _ in database.IMPORT_FIELDS]
        labels += [(key, row[key]) for key in ("source_page", "source_table", "extraction_method")]
        body = "\n".join(f"{name}: {value if value is not None else 'not recorded'}" for name, value in labels)
        body += ("\nCSV status: present in latest import" if row["source_row"] is not None else
                 "\nCSV status: retained from earlier import; absent from latest CSV")
        for part, text in enumerate(_parts(body)):
            chunks.append({"id": f"experiment_{row['id']}_{part}",
                "text": f"Experiment {row['id']}. Source: {paper['title']}\n{text}",
                "metadata": {"source_doi": paper["doi"], "source_title": paper["title"],
                             "experiment_id": row["id"], "chunk_type": "experiment"}})
    for path in sorted(Path(raw_texts_dir).glob("*.txt")):
        source = "project-background-note" if path.stem == "project_background_note" else path.stem
        for part, text in enumerate(_parts(path.read_text(encoding="utf-8"))):
            chunks.append({"id": f"text_{hashlib.sha256(path.name.encode()).hexdigest()}_{part}",
                           "text": text, "metadata": {"source_doi": source,
                           "source_title": path.stem, "chunk_type": "fulltext"}})
    digest = hashlib.sha256(json.dumps([FORMAT_VERSION, EMBEDDING_MODEL, chunks],
                                      sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return digest, chunks


def _manifest(chroma_dir):
    try:
        value = json.loads((Path(chroma_dir) / "active_index.json").read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def status(database_path=database.DEFAULT_DATABASE, chroma_dir=CHROMA_DIR, raw_texts_dir=RAW_TEXTS_DIR):
    digest, chunks = snapshot(database_path, raw_texts_dir)
    manifest = _manifest(chroma_dir)
    current = manifest.get("digest") == digest and bool(manifest.get("collection"))
    return {"current": current, "chunks": len(chunks), "digest": digest, "manifest": manifest}


@lru_cache(maxsize=1)
def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBEDDING_MODEL)


def get_client(chroma_dir):
    import chromadb
    return chromadb.PersistentClient(path=str(chroma_dir))


def rebuild(database_path=database.DEFAULT_DATABASE, chroma_dir=CHROMA_DIR,
            raw_texts_dir=RAW_TEXTS_DIR, *, client=None, model=None):
    digest, chunks = snapshot(database_path, raw_texts_dir)
    client = client if client is not None else get_client(chroma_dir)
    name = "pyrolytic_" + uuid.uuid4().hex
    collection = client.create_collection(name, embedding_function=None,
                                          metadata={"hnsw:space": "cosine", "digest": digest})
    if chunks:
        model = model if model is not None else get_model()
        for start in range(0, len(chunks), 32):
            batch = chunks[start:start + 32]
            texts = [chunk["text"] for chunk in batch]
            vectors = model.encode(texts, show_progress_bar=False).tolist()
            collection.upsert(ids=[chunk["id"] for chunk in batch], documents=texts,
                              embeddings=vectors, metadatas=[chunk["metadata"] for chunk in batch])
    if collection.count() != len(chunks):
        raise RuntimeError("Index is incomplete. The previous index remains selected.")
    if snapshot(database_path, raw_texts_dir)[0] != digest:
        raise RuntimeError("Sources changed during indexing. Rebuild again before using live chat.")
    manifest = {"digest": digest, "collection": name, "chunks": len(chunks), "model": EMBEDDING_MODEL}
    directory = Path(chroma_dir)
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory,
                                     suffix=".json", delete=False) as temporary:
        json.dump(manifest, temporary)
        temporary_path = temporary.name
    os.replace(temporary_path, directory / "active_index.json")
    return manifest


def search(query, k=5, database_path=database.DEFAULT_DATABASE, chroma_dir=CHROMA_DIR,
           raw_texts_dir=RAW_TEXTS_DIR, *, client=None, model=None):
    if not isinstance(k, int) or isinstance(k, bool) or k < 1:
        raise ValueError("k must be a positive integer")
    info = status(database_path, chroma_dir, raw_texts_dir)
    if not info["current"]:
        raise ValueError("Search index is missing or outdated. Use Rebuild search index before live chat.")
    client = client if client is not None else get_client(chroma_dir)
    collection = client.get_collection(info["manifest"]["collection"], embedding_function=None)
    count = collection.count()
    if count != info["chunks"] or (collection.metadata or {}).get("digest") != info["digest"]:
        raise ValueError("Search index is incomplete. Rebuild search index before live chat.")
    if count == 0:
        return []
    model = model if model is not None else get_model()
    result = collection.query(query_embeddings=model.encode([query]).tolist(), n_results=min(k, count))
    if snapshot(database_path, raw_texts_dir)[0] != info["digest"]:
        raise ValueError("Sources changed during search. Rebuild the index and retry.")
    return [{"text": text, **metadata, "distance": distance} for text, metadata, distance in
            zip(result["documents"][0], result["metadatas"][0], result["distances"][0])]


def render():
    import streamlit as st
    st.subheader("Chat search index")
    try:
        info = status()
    except (OSError, sqlite3.Error, ValueError) as error:
        st.error(f"Cannot inspect search sources: {error}")
        return
    st.caption(f"{info['chunks']} searchable chunks from the database and local texts.")
    if info["current"]:
        st.caption("Index matches the current sources.")
    else:
        st.info("Search index needs rebuilding before live chat can use the current data.")
    st.caption("First rebuild downloads the embedding model. Experiment data is embedded locally. "
               "Retained experiments from older CSV imports are included.")
    if st.button("Rebuild search index", key="rebuild_search_index"):
        try:
            with st.spinner("Building search index from current sources..."):
                rebuild()
        except Exception as error:
            st.error(f"Rebuild failed: {error}")
        else:
            st.rerun()
