from dataclasses import dataclass, field
from app.models.ir.project_snapshot_ir import ParsedProjectIR
from app.models.ir.class_ir import ClassIR
from app.models.ir.function_ir import FunctionIR
from app.models.ir.file_ir import FileIR

@dataclass
class CodeChunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)

def _build_function_text(func: FunctionIR, class_name: str = None) -> str:
    """Build rich text for a function/method chunk."""
    parts = []
    if class_name:
        parts.append(f"Class: {class_name}")
    parts.append(f"Function: {func.name}")
    if func.docstring:
        parts.append(f"Docstring: {func.docstring.text}")
    params = ", ".join(p.name for p in func.parameters)
    parts.append(f"Parameters: {params}")
    if func.source_code:
        parts.append(f"Source:\n{func.source_code}")
    return "\n".join(parts)

def _build_class_text(cls: ClassIR) -> str:
    """Build rich text for a class chunk."""
    parts = [f"Class: {cls.name}"]
    if cls.bases:
        parts.append(f"Inherits: {', '.join(cls.bases)}")
    if cls.docstring:
        parts.append(f"Docstring: {cls.docstring.text}")
    methods = ", ".join(m.name for m in cls.methods)
    parts.append(f"Methods: {methods}")
    if cls.source_code:
        parts.append(f"Source:\n{cls.source_code}")
    return "\n".join(parts)

def _build_file_text(file_ir: FileIR) -> str:
    """Build rich text for a file chunk."""
    parts = [f"File: {file_ir.path}", f"Module: {file_ir.module}"]
    if file_ir.source_code:
        parts.append(f"Source:\n{file_ir.source_code[:2000]}")
    return "\n".join(parts)

def create_chunks(parsed_project: ParsedProjectIR, project_id: str) -> list[CodeChunk]:
    """Convert a ParsedProjectIR into semantic code chunks with deduplication."""
    chunks: list[CodeChunk] = []
    seen_ids: set[str] = set()  # 👈 Track seen IDs to prevent duplicates
    
    def add_chunk(chunk: CodeChunk):
        """Add chunk only if ID hasn't been seen."""
        if chunk.id not in seen_ids:
            chunks.append(chunk)
            seen_ids.add(chunk.id)
    
    # Build lookup maps
    file_map = {f.id: f for f in parsed_project.files}
    class_map = {c.id: c for c in parsed_project.classes}
    
    # 1. File-level chunks
    for file_ir in parsed_project.files:
        if not file_ir.source_code:
            continue
        add_chunk(CodeChunk(
            id=f"file_{file_ir.id}",
            text=_build_file_text(file_ir),
            metadata={
                "type": "file",
                "project_id": project_id,
                "file_path": file_ir.path,
                "file_id": file_ir.id,
                "module": file_ir.module,
            }
        ))
    
    # 2. Class-level chunks
    for cls in parsed_project.classes:
        if not cls.source_code:
            continue
        file_ir = file_map.get(cls.file_id)
        add_chunk(CodeChunk(
            id=f"class_{cls.id}",
            text=_build_class_text(cls),
            metadata={
                "type": "class",
                "project_id": project_id,
                "name": cls.name,
                "file_path": file_ir.path if file_ir else "",
                "file_id": cls.file_id,
                "class_id": cls.id,
                "lineno": cls.lineno,
            }
        ))
    
    # 3. Module-level function chunks
    for func in parsed_project.functions:
        if not func.source_code:
            continue
        file_ir = file_map.get(func.file_id)
        add_chunk(CodeChunk(
            id=f"func_{func.id}",
            text=_build_function_text(func),
            metadata={
                "type": "function",
                "project_id": project_id,
                "name": func.name,
                "file_path": file_ir.path if file_ir else "",
                "file_id": func.file_id,
                "function_id": func.id,
                "lineno": func.lineno,
            }
        ))
    
    # 4. Method chunks (functions inside classes)
    for cls in parsed_project.classes:
        file_ir = file_map.get(cls.file_id)
        for method in cls.methods:
            if not method.source_code:
                continue
            add_chunk(CodeChunk(
                id=f"method_{method.id}",
                text=_build_function_text(method, class_name=cls.name),
                metadata={
                    "type": "method",
                    "project_id": project_id,
                    "name": method.name,
                    "class_name": cls.name,
                    "class_id": cls.id,
                    "file_path": file_ir.path if file_ir else "",
                    "file_id": cls.file_id,
                    "function_id": method.id,
                    "lineno": method.lineno,
                }
            ))
    
    return chunks