import ast

def parse_bases(bases: list[ast.expr]) -> list[str]:
    return [ast.unparse(base) for base in bases]