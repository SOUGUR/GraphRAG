import ast
from app.models.ir.variable_ir import VariableIR

def parse_variables(body: list[ast.stmt], scope: str) -> list[VariableIR]:
    variables = []
    for stmt in body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            variables.append(VariableIR(
                name=stmt.target.id,
                type_hint=ast.unparse(stmt.annotation) if stmt.annotation else None,
                value=ast.unparse(stmt.value) if stmt.value else None,
                scope=scope
            ))
        elif isinstance(stmt, ast.Assign):
            value = ast.unparse(stmt.value) if stmt.value else None
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    variables.append(VariableIR(
                        name=target.id, type_hint=None, value=value, scope=scope
                    ))
    return variables