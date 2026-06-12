"""Milestone 5 — Grounded generation.

Takes a query plus the chunks from retrieve() and asks Groq's
llama-3.3-70b-versatile to answer using ONLY that retrieved context. The system
prompt enforces grounding (no outside knowledge), balanced synthesis across
reviews for subjective questions, and an honest fallback when the context is
thin. Sources are appended as a citation list built from chunk metadata.

Run standalone for a quick end-to-end check:  python generator.py
"""

from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)

NO_CONTEXT_MSG = (
    "I don't have anything about that in my sources on University View. "
    "Try rephrasing, or ask about pricing, location, amenities, or what "
    "residents say about living there."
)

SYSTEM_PROMPT = """You are The Unofficial Guide to University View, a student \
apartment complex near the University of Maryland. You answer questions using \
ONLY the CONTEXT passages provided below, which come from reviews, listings, \
and the official FAQ.

Rules:
- Answer strictly from the CONTEXT. Do NOT use any outside knowledge about \
University View or apartments in general.
- If the CONTEXT does not contain the answer, say so plainly — do not guess. \
An honest "the sources don't cover that" is better than a confident guess.
- For subjective questions (e.g. "is it worth it?", "what are the downsides?"), \
synthesize a balanced view across the different sources rather than quoting one. \
Note when sources disagree.
- Be concise and specific. Quote concrete figures (prices, distances, dates) \
when the context provides them.
- Do not invent URLs or sources. The interface appends citations for you.
- If there's a generic question about prices, clearly state that it varies but
give a reference point for what a normal apartment would cost given x and y 
number of beds and baths.
- If the question feels vague, then ask 2 clarifying questions before giving 
a response. """


def _format_context(chunks: list[dict]) -> str:
    """Build a labeled context block; each chunk tagged with its source."""
    blocks = []
    for i, c in enumerate(chunks, 1):
        blocks.append(f"[{i}] (Source: {c['source']})\n{c['text']}")
    return "\n\n".join(blocks)


def _format_sources(chunks: list[dict]) -> str:
    """Deduplicated 'Sources:' list with URLs, preserving retrieval order."""
    seen = {}
    for c in chunks:
        if c["source"] not in seen:
            seen[c["source"]] = c["url"]
    lines = [f"- {name}{(' — ' + url) if url else ''}" for name, url in seen.items()]
    return "Sources:\n" + "\n".join(lines)


def generate_response(query: str, retrieved_chunks: list[dict]) -> str:
    """Generate a grounded, cited answer string from retrieved chunks."""
    if not retrieved_chunks:
        return NO_CONTEXT_MSG

    user_msg = (
        f"CONTEXT:\n{_format_context(retrieved_chunks)}\n\n"
        f"QUESTION: {query}\n\n"
        "Answer using only the context above."
    )
    completion = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )
    answer = completion.choices[0].message.content.strip()
    return f"{answer}\n\n{_format_sources(retrieved_chunks)}"


if __name__ == "__main__":
    from retriever import retrieve
    q = "How close is it to campus?"
    print(f"Q: {q}\n")
    print(generate_response(q, retrieve(q)))
