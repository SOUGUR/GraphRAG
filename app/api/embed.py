from fastapi import APIRouter, HTTPException, Path as PathParam
from app.services.embedding_service import EmbeddingService

router = APIRouter()

@router.post("/embed/{project_id}")
async def embed_project(project_id: str = PathParam(...)):
    try:
        service = EmbeddingService(project_id)
        result = service.embed_project()
        return {"status": "success", **result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")