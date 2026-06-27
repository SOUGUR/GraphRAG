from app.services.ingest_service import IngestService
from app.graph.graph_builder import GraphBuilder

class GraphService:
    def __init__(self, project_id: str):
        self.project_id = project_id
        
    def build_graph(self) -> dict:
        # 1. Parse project into IR
        ingest_service = IngestService(self.project_id)
        parsed_ir = ingest_service.parse_project()
        
        # 2. Build Graph in Neo4j
        builder = GraphBuilder(parsed_ir)
        builder.build()
        
        return {
            "files": len(parsed_ir.files),
            "classes": len(parsed_ir.classes),
            "functions": len(parsed_ir.functions) + sum(len(c.methods) for c in parsed_ir.classes)
        }