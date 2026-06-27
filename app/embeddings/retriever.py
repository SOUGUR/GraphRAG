from langchain_chroma import Chroma
from app.embeddings.vector_store import get_vector_store
from app.config.settings import TOP_K_VECTOR

def vector_search(query: str, project_id: str, k: int = TOP_K_VECTOR) -> list[dict]:
    """Basic vector similarity search scoped to a project."""
    store: Chroma = get_vector_store()
    results = store.similarity_search_with_score(
        query=query,
        k=k,
        filter={"project_id": project_id},
    )
    output = []
    for doc, score in results:
        output.append({
            "id": doc.id,
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score),  # Lower is better in Chroma (L2 distance)
        })
    return output