import ast
from app.models.ir.class_ir import ClassIR
from app.models.ir.docstring_ir import DocstringIR
from app.parser.decorator_parser import parse_decorators
from app.parser.inheritance_parser import parse_bases
from app.parser.function_parser import parse_functions
from app.parser.variable_parser import parse_variables

def parse_classes(body: list[ast.stmt]) -> list[ClassIR]:
    classes = []
    for stmt in body:
        if isinstance(stmt, ast.ClassDef):
            docstring = None
            if (stmt.body and isinstance(stmt.body[0], ast.Expr) and 
                isinstance(stmt.body[0].value, ast.Constant) and isinstance(stmt.body[0].value.value, str)):
                docstring = DocstringIR(text=stmt.body[0].value.value)
                
            classes.append(ClassIR(
                name=stmt.name, lineno=stmt.lineno, end_lineno=stmt.end_lineno,
                bases=parse_bases(stmt.bases), decorators=parse_decorators(stmt.decorator_list),
                methods=parse_functions(stmt.body, scope="class"),
                variables=parse_variables(stmt.body, scope="class"), docstring=docstring
            ))
    return classes