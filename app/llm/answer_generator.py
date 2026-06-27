import time
from functools import wraps
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from app.config.settings import GOOGLE_API_KEY, LLM_MODEL
from app.llm.prompts import QUERY_PROMPT

def retry_with_backoff(max_retries=3, initial_delay=2.0):
    """Decorator to retry API calls with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_msg = str(e).lower()
                    # Check if it's a rate limit error
                    if "429" in error_msg or "resource_exhausted" in error_msg or "quota" in error_msg:
                        if attempt == max_retries - 1:
                            raise
                        print(f"⚠️ Rate limit hit. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        # Not a rate limit error, raise immediately
                        raise
            return None
        return wrapper
    return decorator

def get_llm():
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.3,
        max_tokens=1000,  # Reduced to save tokens
    )

def format_context(retrieved_chunks: list[dict]) -> str:
    """Format retrieved chunks into a readable context string."""
    if not retrieved_chunks:
        return "No relevant code found."
    
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        meta = chunk.get("metadata", {})
        chunk_type = meta.get("type", "unknown")
        name = meta.get("name") or meta.get("file_path", "unknown")
        text = chunk.get("text", "")
        
        # Truncate very long code snippets
        if len(text) > 1000:
            text = text[:1000] + "... [truncated]"
        
        context_parts.append(f"\n--- Snippet {i} ({chunk_type}: {name}) ---\n{text}\n")
    
    return "\n".join(context_parts)

@retry_with_backoff(max_retries=3, initial_delay=2.0)
def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    """Generate a natural language answer using Gemini with retry logic."""
    llm = get_llm()
    context = format_context(retrieved_chunks)
    
    chain = QUERY_PROMPT | llm | StrOutputParser()
    
    response = chain.invoke({
        "query": query,
        "context": context,
    })
    
    return response