from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from app.config.settings import GROQ_API_KEY, LLM_MODEL
from app.llm.prompts import QUERY_PROMPT

def get_llm():
    return ChatGroq(
        model=LLM_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=0.3,
        max_tokens=2000,
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
        
        context_parts.append(f"\n--- Snippet {i} ({chunk_type}: {name}) ---\n{text}\n")
    
    return "\n".join(context_parts)

def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    """Generate a natural language answer using Groq (Llama 3)."""
    llm = get_llm()
    context = format_context(retrieved_chunks)
    
    chain = QUERY_PROMPT | llm | StrOutputParser()
    
    response = chain.invoke({
        "query": query,
        "context": context,
    })
    
    return response