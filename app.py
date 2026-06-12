"""Milestone 5 — Query interface.

Gradio chat UI that wires the pipeline together:
    user message -> retrieve() -> generate_response() -> grounded, cited answer

On startup the corpus is indexed if the vector store is empty. To force a
rebuild after adding/removing source documents, run `python retriever.py`.

Run:  python app.py   (then open the printed local URL)
"""

import gradio as gr

from generator import generate_response
from retriever import ensure_indexed, retrieve

EXAMPLES = [
    "What are the monthly costs and fees?",
    "Is it worth it?",
    "How close is it to campus?",
    "What are the downsides?",
    "What's included?",
]

DESCRIPTION = (
    "Ask about **University View** (UMD off-campus housing). Answers are drawn "
    "only from collected reviews, listings, and the official FAQ — each response "
    "lists its sources. If the sources don't cover something, the bot says so."
)


def chat(message: str, history) -> str:
    """Gradio chat handler: retrieve relevant chunks, then generate an answer."""
    if not message or not message.strip():
        return "Ask me something about University View."
    chunks = retrieve(message)
    return generate_response(message, chunks)


def build_demo() -> gr.ChatInterface:
    return gr.ChatInterface(
        fn=chat,
        title="The Unofficial Guide — University View",
        description=DESCRIPTION,
        examples=EXAMPLES,
    )


if __name__ == "__main__":
    ensure_indexed()
    build_demo().launch()
