"""Central configuration for the RAG pipeline."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM (Groq) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"

# --- Embeddings ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Vector store ---
CHROMA_COLLECTION = "unofficial_guide"
CHROMA_PATH = "./chroma_db"

# --- Retrieval ---
N_RESULTS = 4          # top-k chunks returned per query
# Cosine distance ceiling; weaker matches are filtered out. Calibrated against
# the 5 eval questions: short subjective queries ("is it worth it?") embed
# ~0.63–0.69 from their answer chunks, so 0.5 produced false "no answer"
# responses. 0.7 recovers them while a cleanly off-topic query still returns [].
MAX_DISTANCE = 0.7
