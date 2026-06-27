import ast
from app.models.ir.call_ir import CallIR

def parse_calls(node: ast.AST, caller_name: str) -> list[CallIR]:
    calls = []
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            calls.append(CallIR(
                caller=caller_name,
                callee=ast.unparse(child.func),
                lineno=child.lineno
            ))
    return calls