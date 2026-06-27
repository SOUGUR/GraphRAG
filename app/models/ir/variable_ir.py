from typing import Optional
from app.models.ir.base_ir import BaseIR

class VariableIR(BaseIR):
    name: str
    type_hint: Optional[str] = None
    value: Optional[str] = None
    scope: str
    file_id: str = ""        
    parent_id: Optional[str] = None  