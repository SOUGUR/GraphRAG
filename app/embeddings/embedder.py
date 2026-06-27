from functools import lru_cache
from langchain_cohere import CohereEmbeddings
from app.config.settings import COHERE_API_KEY, EMBEDDING_MODEL

@lru_cache(maxsize=1)
def get_embedder() -> CohereEmbeddings:
    """Singleton Cohere embedder (Generous free tier: 100 calls/min)."""
    if not COHERE_API_KEY:
        raise ValueError("COHERE_API_KEY not set in .env")
    return CohereEmbeddings(
        model=EMBEDDING_MODEL,
        cohere_api_key=COHERE_API_KEY,
    )