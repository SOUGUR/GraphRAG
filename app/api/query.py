from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Path as PathParam
from app.services.query_service import QueryService

router = APIRouter()

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    top_n: int = Field(default=5, ge=1, le=20)
    use_llm: bool = Field(default=True, description="Generate answer with LLM")

@router.post("/query/{project_id}")
async def query_project(project_id: str = PathParam(...), body: QueryRequest = ...):
    try:
        service = QueryService(project_id)
        
        if body.use_llm:
            # Full pipeline with LLM
            result = service.query_with_llm(body.query, top_n=body.top_n)
            return {
                "project_id": project_id,
                "query": body.query,
                "answer": result["answer"],
                "sources": result["retrieved_chunks"],
                "source_count": result["chunk_count"],
            }
        else:
            # Just retrieval
            results = service.retrieve(body.query, top_n=body.top_n)
            return {
                "project_id": project_id,
                "query": body.query,
                "count": len(results),
                "results": results,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")