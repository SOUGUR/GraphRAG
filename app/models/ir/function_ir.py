from typing import Optional
from pydantic import Field
from app.models.ir.base_ir import BaseIR
from app.models.ir.parameter_ir import ParameterIR
from app.models.ir.variable_ir import VariableIR
from app.models.ir.decorator_ir import DecoratorIR
from app.models.ir.call_ir import CallIR
from app.models.ir.return_ir import ReturnIR
from app.models.ir.docstring_ir import DocstringIR

class FunctionIR(BaseIR):
    name: str
    lineno: int
    end_lineno: int
    file_id: str = "" 
    parent_id: Optional[str] = None
    source_code: str = "" 
    is_async: bool = False
    parameters: list[ParameterIR] = Field(default_factory=list)
    decorators: list[DecoratorIR] = Field(default_factory=list)
    variables: list[VariableIR] = Field(default_factory=list)
    calls: list[CallIR] = Field(default_factory=list)
    returns: Optional[ReturnIR] = None
    docstring: Optional[DocstringIR] = None