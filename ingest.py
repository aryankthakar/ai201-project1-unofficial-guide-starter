"""Milestone 3b — Chunking.

Loads the cleaned Markdown produced by scrape.py and splits each document into
overlapping chunks ready for embedding.

Chunking strategy (uniform sliding window over characters):
  - size    = 400 chars  : a review-heavy corpus packs one opinion / one FAQ
                           answer into a short span; small chunks keep each
                           retrieved unit focused on a single perspective and
                           stay well under MiniLM's 256-token (~1000 char) limit
                           so nothing is silently truncated at embed time.
  - overlap = 75 chars   : protects rules/answers that straddle a boundary.
  - min_len = 50 chars   : trailing fragments shorter than this are discarded.

Each chunk carries its source title + url so retrieval can attribute answers.

Run standalone to see corpus stats:  python ingest.py
"""

from pathlib import Path

CHUNK_SIZE = 400
CHUNK_OVERLAP = 75
MIN_CHUNK_LEN = 50

HERE = Path(__file__).parent
DOCS = HERE / "documents"


def load_markdown(docs_dir: Path = DOCS) -> list[dict]:
    """Load every documents/*.md (skipping raw/), parsing front-matter.

    Returns a list of {"name", "source", "url", "text"} dicts.
    """
    docs = []
    for path in sorted(docs_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        source, url, body = _parse_front_matter(raw)
        docs.append({
            "name": path.stem,
            "source": source or path.stem,
            "url": url or "",
            "text": body,
        })
    return docs


def _parse_front_matter(raw: str) -> tuple[str, str, str]:
    """Split a '---\\nsource: ..\\nurl: ..\\n---\\n\\n<body>' file into parts."""
    if not raw.startswith("---"):
        return "", "", raw.strip()
    _, fm, body = raw.split("---", 2)
    source = url = ""
    for line in fm.strip().splitlines():
        if line.startswith("source:"):
            source = line.split(":", 1)[1].strip()
        elif line.startswith("url:"):
            url = line.split(":", 1)[1].strip()
    return source, url, body.strip()


def chunk_text(text: str, meta: dict,
               size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP,
               min_len: int = MIN_CHUNK_LEN) -> list[dict]:
    """Split one document's text into overlapping chunks.

    Each chunk = {"text", "source", "url", "chunk_id"}. chunk_id is unique:
    "<name>_<index>". Whitespace-only or sub-min_len chunks are dropped.
    """
    step = size - overlap
    chunks = []
    idx = 0
    for start in range(0, len(text), step):
        piece = text[start:start + size].strip()
        if len(piece) < min_len:
            continue
        chunks.append({
            "text": piece,
            "source": meta["source"],
            "url": meta["url"],
            "chunk_id": f"{meta['name']}_{idx}",
        })
        idx += 1
    return chunks


def build_chunks(docs_dir: Path = DOCS) -> list[dict]:
    """Load all docs and return the full list of chunks across the corpus."""
    all_chunks = []
    for doc in load_markdown(docs_dir):
        all_chunks.extend(chunk_text(doc["text"], doc))
    return all_chunks


def main() -> None:
    docs = load_markdown()
    print(f"Loaded {len(docs)} documents from {DOCS}/\n")
    total = 0
    lengths = []
    for doc in docs:
        chunks = chunk_text(doc["text"], doc)
        total += len(chunks)
        lengths += [len(c["text"]) for c in chunks]
        print(f"  {doc['name']:<24} {len(doc['text']):>7} chars -> {len(chunks):>3} chunks")
    avg = sum(lengths) / len(lengths) if lengths else 0
    print(f"\nTotal: {total} chunks, avg {avg:.0f} chars/chunk")
    print("\n--- sample chunk ---")
    sample = build_chunks()
    if sample:
        c = sample[len(sample) // 2]
        print(f"[{c['chunk_id']}] ({c['source']})\n{c['text'][:300]}")


if __name__ == "__main__":
    main()
