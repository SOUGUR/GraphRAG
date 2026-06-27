from app.models.ir.base_ir import BaseIR

class CallIR(BaseIR):
    caller: str
    callee: str
    lineno: int