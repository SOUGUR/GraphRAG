import ast
from app.models.ir.import_ir import ImportIR

def parse_imports(body: list[ast.stmt]) -> list[ImportIR]:
    imports = []
    for stmt in body:
        if isinstance(stmt, ast.Import):
            for alias in stmt.names:
                imports.append(ImportIR(module=alias.name, name=alias.name, alias=alias.asname))
        elif isinstance(stmt, ast.ImportFrom):
            for alias in stmt.names:
                imports.append(ImportIR(
                    module=stmt.module or "", name=alias.name, alias=alias.asname,
                    is_relative=(stmt.level > 0), level=stmt.level
                ))
    return imports