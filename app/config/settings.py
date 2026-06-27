from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Upload configurations
UPLOAD_DIR = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {".py"}
IGNORE_DIRS = {
    "__pycache__", ".git", "venv", "env", ".venv", 
    "node_modules", ".idea", ".vscode", "dist", "build"
}

# Ensure the uploads directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


# ---Gemini ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# EMBEDDING_MODEL = "gemini-embedding-001"
# LLM_MODEL = "gemini-2.0-flash"

LLM_MODEL = "llama-3.3-70b-versatile"  
EMBEDDING_MODEL = "embed-english-v3.0" # Cohere model


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# --- ChromaDB ---
CHROMA_DIR = BASE_DIR / "chroma_db"
CHROMA_COLLECTION = "code_chunks"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ---Retrieval ---
# Change these settings in app/config/settings.py
TOP_K_VECTOR = 5        # Reduced from 10
TOP_K_GRAPH = 5         # Reduced from 10
RERANK_TOP_N = 3        # Reduced from 5
HYBRID_ALPHA = 0.6        # 0.6 vector + 0.4 graph
