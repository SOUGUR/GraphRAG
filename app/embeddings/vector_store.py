from functools import lru_cache
import time
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.config.settings import CHROMA_DIR, CHROMA_COLLECTION
from app.embeddings.embedder import get_embedder

@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    """Singleton Chroma vector store."""
    return Chroma(
        collection_name=CHROMA_COLLECTION,
        embedding_function=get_embedder(),
        persist_directory=str(CHROMA_DIR),
    )

def add_chunks(chunks: list, batch_size: int = 5) -> int:
    """Add CodeChunks to Chroma in batches to avoid rate limits."""
    if not chunks:
        return 0
    
    store = get_vector_store()
    documents = [
        Document(
            page_content=c.text,
            metadata=c.metadata,
            id=c.id,
        )
        for c in chunks
    ]
    
    # Process in small batches with delays
    total_added = 0
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        try:
            store.add_documents(batch)
            total_added += len(batch)
        except Exception as e:
            print(f"Batch failed: {e}, retrying...")
            time.sleep(3)  # Wait before retry
            try:
                store.add_documents(batch)
                total_added += len(batch)
            except Exception:
                pass  # Skip failed batch
        
        # Add delay between batches to avoid rate limits
        if i + batch_size < len(documents):
            time.sleep(2)  # 2 second pause between batches
    
    return total_added

def delete_project_chunks(project_id: str) -> None:
    """Remove all chunks belonging to a project."""
    store = get_vector_store()
    try:
        store.delete(filter={"project_id": project_id})
    except Exception:
        pass