from app.services.ingest_service import IngestService
from app.embeddings.chunker import create_chunks
from app.embeddings.vector_store import add_chunks, delete_project_chunks

class EmbeddingService:
    def __init__(self, project_id: str):
        self.project_id = project_id

    def embed_project(self) -> dict:
        # 1. Parse project (reuses IR from Step 2)
        ingest = IngestService(self.project_id)
        parsed = ingest.parse_project()

        # 2. Remove stale chunks for this project
        delete_project_chunks(self.project_id)

        # 3. Chunk + embed + store
        chunks = create_chunks(parsed, self.project_id)
        added = add_chunks(chunks)

        return {
            "project_id": self.project_id,
            "chunks_created": added,
            "files": len(parsed.files),
            "classes": len(parsed.classes),
            "functions": len(parsed.functions) + sum(len(c.methods) for c in parsed.classes),
        }