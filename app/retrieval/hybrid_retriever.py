from app.config.settings import HYBRID_ALPHA, TOP_K_VECTOR, TOP_K_GRAPH, RERANK_TOP_N
from app.retrieval.vector_retriever import retrieve_vectors
from app.retrieval.graph_retriever import graph_search
from app.retrieval.reranker import rerank

def _merge(vector_results: list[dict], graph_results: list[dict], alpha: float) -> list[dict]:
    """
    Merge vector + graph results using Reciprocal Rank Fusion + weighted score.
    alpha = weight for vector (1-alpha for graph).
    """
    merged: dict[str, dict] = {}

    # Vector contribution (rank-based)
    for rank, item in enumerate(vector_results):
        cid = item["id"]
        if cid not in merged:
            merged[cid] = {**item, "hybrid_score": 0.0}
        # RRF: 1 / (k + rank), k=60 is standard
        rrf = 1.0 / (60 + rank)
        merged[cid]["hybrid_score"] += alpha * rrf
        merged[cid]["metadata"]["vector_score"] = item.get("score", 0.0)

    # Graph contribution
    for rank, item in enumerate(graph_results):
        cid = item["id"]
        if cid not in merged:
            merged[cid] = {**item, "hybrid_score": 0.0}
        rrf = 1.0 / (60 + rank)
        merged[cid]["hybrid_score"] += (1 - alpha) * rrf
        merged[cid]["metadata"]["graph_score"] = item.get("score", 0.0)

    # Sort by hybrid score
    return sorted(merged.values(), key=lambda x: x["hybrid_score"], reverse=True)

def hybrid_retrieve(
    query: str,
    project_id: str,
    k_vector: int = TOP_K_VECTOR,
    k_graph: int = TOP_K_GRAPH,
    alpha: float = HYBRID_ALPHA,
    rerank_n: int = RERANK_TOP_N,
    use_reranker: bool = True,
) -> list[dict]:
    """Full hybrid retrieval pipeline: vector + graph + rerank."""
    vector_results = retrieve_vectors(query, project_id, k=k_vector)
    graph_results = graph_search(query, project_id, k=k_graph)

    merged = _merge(vector_results, graph_results, alpha)

    if use_reranker and merged:
        merged = rerank(query, merged, top_n=rerank_n)
    else:
        merged = merged[:rerank_n]

    return merged