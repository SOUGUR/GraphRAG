import ast
from app.models.ir.decorator_ir import DecoratorIR

def parse_decorators(decorator_list: list[ast.expr]) -> list[DecoratorIR]:
    return [DecoratorIR(name=ast.unparse(dec)) for dec in decorator_list]