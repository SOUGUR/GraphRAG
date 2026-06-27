from typing import Optional
from app.models.ir.base_ir import BaseIR

class ReturnIR(BaseIR):
    annotation: Optional[str] = None