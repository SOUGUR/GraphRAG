from typing import Optional
from app.models.ir.base_ir import BaseIR

class ParameterIR(BaseIR):
    name: str
    annotation: Optional[str] = None
    default: Optional[str] = None