import ast
import hashlib
from pathlib import Path
from typing import Tuple, List
from app.models.ir.file_ir import FileIR
from app.models.ir.import_ir import ImportIR
from app.models.ir.class_ir import ClassIR
from app.models.ir.function_ir import FunctionIR
from app.models.ir.variable_ir import VariableIR
from app.parser.import_parser import parse_imports
from app.parser.class_parser import parse_classes
from app.parser.function_parser import parse_functions
from app.parser.variable_parser import parse_variables

def _extract_source(source_lines: list[str], node: ast.AST) -> str:
    """Extract source code slice using AST line numbers."""
    if hasattr(node, "end_lineno") and node.end_lineno:
        return "".join(source_lines[node.lineno - 1:node.end_lineno])
    return ""

def parse_file(file_path: Path, project_root: Path) -> Tuple[
    FileIR, List[ImportIR], List[ClassIR], List[FunctionIR], List[VariableIR]
]:
    source_code = file_path.read_text(encoding="utf-8")
    source_lines = source_code.splitlines(keepends=True)
    tree = ast.parse(source_code, filename=str(file_path))
    
    rel_path = file_path.relative_to(project_root)
    module_name = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
    if module_name.endswith(".__init__"): 
        module_name = module_name[:-9]
        
    file_ir = FileIR(
        name=file_path.name, path=str(rel_path), extension=file_path.suffix,
        size=file_path.stat().st_size, lines_of_code=len(source_code.splitlines()),
        sha256=hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        module=module_name, source_code=source_code
    )
    
    imports = parse_imports(tree.body)
    classes = parse_classes(tree.body)
    functions = parse_functions(tree.body, scope="module")
    variables = parse_variables(tree.body, scope="module")
    
    # Inject source code into classes and functions
    for cls in classes:
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == cls.name:
                cls.source_code = _extract_source(source_lines, node)
                break
        for method in cls.methods:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method.name:
                    method.source_code = _extract_source(source_lines, node)
                    break
    
    for func in functions:
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func.name:
                func.source_code = _extract_source(source_lines, node)
                break
    
    return file_ir, imports, classes, functions, variables