from fastapi import APIRouter, HTTPException, Path as PathParam
from app.services.graph_service import GraphService

router = APIRouter()

@router.post("/build-graph/{project_id}")
async def build_graph(project_id: str = PathParam(...)):
    try:
        service = GraphService(project_id)
        stats = service.build_graph()
        
        return {
            "project_id": project_id,
            "status": "success",
            "message": "Graph built and stored in Neo4j successfully.",
            "stats": stats
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building graph: {str(e)}")