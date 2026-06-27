import ast
from typing import Optional
from app.models.ir.function_ir import FunctionIR
from app.models.ir.parameter_ir import ParameterIR
from app.models.ir.return_ir import ReturnIR
from app.models.ir.docstring_ir import DocstringIR
from app.parser.decorator_parser import parse_decorators
from app.parser.variable_parser import parse_variables
from app.parser.call_parser import parse_calls

def _parse_parameters(args: ast.arguments) -> list[ParameterIR]:
    params = []
    offset = len(args.args) - len(args.defaults)
    for i, arg in enumerate(args.args):
        default_idx = i - offset
        params.append(ParameterIR(
            name=arg.arg,
            annotation=ast.unparse(arg.annotation) if arg.annotation else None,
            default=ast.unparse(args.defaults[default_idx]) if default_idx >= 0 else None
        ))
    if args.vararg:
        params.append(ParameterIR(name=f"*{args.vararg.arg}", annotation=ast.unparse(args.vararg.annotation) if args.vararg.annotation else None))
    if args.kwarg:
        params.append(ParameterIR(name=f"**{args.kwarg.arg}", annotation=ast.unparse(args.kwarg.annotation) if args.kwarg.annotation else None))
    return params

def _parse_returns(returns: Optional[ast.expr]) -> Optional[ReturnIR]:
    return ReturnIR(annotation=ast.unparse(returns)) if returns else None

def parse_functions(body: list[ast.stmt], scope: str = "module") -> list[FunctionIR]:
    functions = []
    for stmt in body:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = None
            if (stmt.body and isinstance(stmt.body[0], ast.Expr) and 
                isinstance(stmt.body[0].value, ast.Constant) and isinstance(stmt.body[0].value.value, str)):
                docstring = DocstringIR(text=stmt.body[0].value.value)
                
            functions.append(FunctionIR(
                name=stmt.name, lineno=stmt.lineno, end_lineno=stmt.end_lineno,
                is_async=isinstance(stmt, ast.AsyncFunctionDef),
                parameters=_parse_parameters(stmt.args),
                decorators=parse_decorators(stmt.decorator_list),
                variables=parse_variables(stmt.body, scope="function"),
                calls=parse_calls(stmt, caller_name=stmt.name),
                returns=_parse_returns(stmt.returns), docstring=docstring
            ))
    return functions