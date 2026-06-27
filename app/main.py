from fastapi import FastAPI
from app.api.routes import api_router

app = FastAPI(
    title="CodeGraphAI",
    description="API for building and querying code knowledge graphs.",
    version="0.1.0 - Step 1"
)

# Include all API routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to CodeGraphAI. Visit /docs for the API documentation."}