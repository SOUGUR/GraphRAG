from app.retrieval.hybrid_retriever import hybrid_retrieve
from app.workflows.query_workflow import query_graph
from app.utils.cache import get_cached_response, cache_response

class QueryService:
    def __init__(self, project_id: str):
        self.project_id = project_id

    def retrieve(self, query: str, top_n: int = 5) -> list[dict]:
        """Basic retrieval without LLM."""
        return hybrid_retrieve(
            query=query,
            project_id=self.project_id,
            rerank_n=top_n,
        )

    def query_with_llm(self, query: str, top_n: int = 5, use_cache: bool = True) -> dict:
        """Full pipeline: retrieve + generate answer using LangGraph."""
        
        # Check cache first
        if use_cache:
            cached = get_cached_response(self.project_id, query, top_n)
            if cached:
                print("✅ Using cached response")
                return cached
        
        initial_state = {
            "project_id": self.project_id,
            "query": query,
            "top_n": top_n,
            "retrieved_chunks": [],
            "answer": "",
        }
        
        final_state = query_graph.invoke(initial_state)
        
        result = {
            "answer": final_state["answer"],
            "retrieved_chunks": final_state["retrieved_chunks"],
            "chunk_count": len(final_state["retrieved_chunks"]),
        }
        
        # Cache the result
        if use_cache:
            cache_response(self.project_id, query, top_n, result)
        
        return result