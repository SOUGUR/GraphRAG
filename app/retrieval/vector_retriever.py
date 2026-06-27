from app.embeddings.retriever import vector_search

def retrieve_vectors(query: str, project_id: str, k: int = 10) -> list[dict]:
    """Project-scoped vector retrieval with normalized scores."""
    raw = vector_search(query, project_id, k=k)
    # Chroma returns L2 distance (lower = better). Convert to similarity.
    if not raw:
        return []
    max_dist = max(r["score"] for r in raw) or 1.0
    for r in raw:
        r["score"] = 1.0 - (r["score"] / (max_dist + 1e-6))
        r["metadata"]["vector_score"] = r["score"]
    return raw