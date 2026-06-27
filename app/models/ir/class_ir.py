from typing import Optional
from pydantic import Field
from app.models.ir.base_ir import BaseIR
from app.models.ir.variable_ir import VariableIR
from app.models.ir.function_ir import FunctionIR
from app.models.ir.decorator_ir import DecoratorIR
from app.models.ir.docstring_ir import DocstringIR

class ClassIR(BaseIR):
    name: str
    lineno: int
    end_lineno: int
    file_id: str = "" 
    source_code: str = "" 
    bases: list[str] = Field(default_factory=list)
    decorators: list[DecoratorIR] = Field(default_factory=list)
    methods: list[FunctionIR] = Field(default_factory=list)
    variables: list[VariableIR] = Field(default_factory=list)
    docstring: Optional[DocstringIR] = None