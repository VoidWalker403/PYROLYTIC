"""Retrieve cited chunks from the current SQLite-backed search snapshot."""

from search_index import search


def retrieve(query, k=5):
    """Return chunk dictionaries with DOI, experiment ID, and cosine distance."""
    return search(query, k)


def format_for_llm_context(results):
    return "\n---\n".join(f"[SOURCE: {row['source_doi']}]\n{row['text']}\n" for row in results)


if __name__ == "__main__":
    for row in retrieve("PP pyrolysis oil yield temperature effects", k=3):
        print(f"[{row['source_doi']}] {row['text']}\n")
