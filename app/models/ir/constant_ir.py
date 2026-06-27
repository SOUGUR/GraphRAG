from typing import Optional
from app.models.ir.base_ir import BaseIR

class ConstantIR(BaseIR):
    name: str
    value: Optional[str] = None