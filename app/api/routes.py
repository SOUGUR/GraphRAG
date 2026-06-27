from fastapi import APIRouter
from app.api import upload, health, graph, embed, query

api_router = APIRouter()

# Register sub-routers with prefixes and tags for Swagger UI
api_router.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
api_router.include_router(health.router, prefix="/api/v1", tags=["Health"])
api_router.include_router(graph.router, prefix="/api/v1", tags=["Graph"])
api_router.include_router(embed.router, prefix="/api/v1", tags=["Embeddings"])
api_router.include_router(query.router, prefix="/api/v1", tags=["Query"])