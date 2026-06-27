
from functools import lru_cache
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config.settings import GOOGLE_API_KEY, EMBEDDING_MODEL

@lru_cache(maxsize=1)
def get_embedder() -> GoogleGenerativeAIEmbeddings:
    """Singleton Gemini embedder with rate limit handling."""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not set in .env")
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
        # Add these parameters for better rate limit handling
        max_retries=3,
        min_retry_seconds=2,
        max_retry_seconds=10,
    )