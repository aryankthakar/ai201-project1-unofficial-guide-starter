"""Milestone 4 — Embedding & retrieval.

Stores chunks in a persistent ChromaDB collection (cosine distance) using the
all-MiniLM-L6-v2 sentence-transformer, and runs semantic search over them.

  - index_corpus()  : (re)build the collection from ingest.build_chunks()
  - retrieve(query) : top-k semantic search, filtered by a cosine-distance
                      ceiling so weak/off-topic matches don't reach the LLM

Run standalone to (re)index and smoke-test a query:  python retriever.py
"""

import chromadb
from chromadb.utils import embedding_functions

from config import (
    CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, MAX_DISTANCE, N_RESULTS,
)
from ingest import build_chunks

# Embedding fn + persistent client initialized once at import.
# sentence-transformers downloads the model on first use (~80MB, one time).
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection."""
    return _collection


def embed_and_store(chunks: list[dict]) -> None:
    """Embed chunks and add them to the collection.

    Metadata stores source title + url so retrieve() can attribute answers.
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"], "url": c["url"]} for c in chunks],
        ids=[c["chunk_id"] for c in chunks],
    )


def index_corpus(reset: bool = True) -> int:
    """Build chunks from documents/ and (re)populate the collection.

    With reset=True the collection is cleared first so re-running after adding
    new source documents fully refreshes the index. Returns the chunk count.
    """
    global _collection
    if reset:
        _client.delete_collection(CHROMA_COLLECTION)
        _collection = _client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            embedding_function=_ef,
            metadata={"hnsw:space": "cosine"},
        )
    chunks = build_chunks()
    if chunks:
        embed_and_store(chunks)
    print(f"Indexed {_collection.count()} chunks into '{CHROMA_COLLECTION}'.")
    return _collection.count()


def ensure_indexed() -> None:
    """Index the corpus only if the collection is empty (used at app startup)."""
    if _collection.count() == 0:
        print("Vector store empty — indexing corpus...")
        index_corpus(reset=False)


def retrieve(query: str, n_results: int = N_RESULTS,
             max_distance: float = MAX_DISTANCE) -> list[dict]:
    """Return the most relevant chunks for a query, filtered by distance.

    Each result: {"text", "source", "url", "distance"}, sorted by ascending
    distance (most similar first). Chunks with distance > max_distance are
    dropped; an empty list means nothing relevant was found.
    """
    if _collection.count() == 0:
        return []

    res = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    # query() nests one list per query; we sent one query -> index [0].
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]

    results = []
    for text, meta, dist in zip(docs, metas, dists):
        if dist > max_distance:
            continue
        results.append({
            "text": text,
            "source": meta.get("source", "unknown"),
            "url": meta.get("url", ""),
            "distance": dist,
        })
    return results


def _probe(query: str) -> None:
    """Print the chunks a query retrieves: raw top-k vs. what passes the filter.

    Shows the cosine distance, source, and full text of each chunk so you can
    judge chunking quality and calibrate MAX_DISTANCE.
    """
    from config import MAX_DISTANCE, N_RESULTS
    raw = retrieve(query, n_results=N_RESULTS, max_distance=99)  # unfiltered
    rule = "─" * 80
    print(f"\nQuery: {query!r}")
    print(f"Top-{N_RESULTS} chunks (filter keeps distance <= {MAX_DISTANCE}):\n")
    for r in raw:
        kept = "KEEP" if r["distance"] <= MAX_DISTANCE else "drop"
        print(rule)
        print(f"[{kept}] dist={r['distance']:.3f}  source={r['source']}")
        print(r["text"])
        print(rule + "\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Probe a specific query without rebuilding the index:
        #   python retriever.py "what are the downsides?"
        _probe(" ".join(sys.argv[1:]))
    else:
        # No args: (re)build the index from documents/.
        index_corpus(reset=True)
