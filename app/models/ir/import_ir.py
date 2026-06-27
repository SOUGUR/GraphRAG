from typing import Optional
from app.models.ir.base_ir import BaseIR

class ImportIR(BaseIR):
    module: Optional[str] = None
    name: str
    alias: Optional[str] = None
    is_relative: bool = False
    level: int = 0