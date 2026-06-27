from app.models.ir.base_ir import BaseIR

class DependencyIR(BaseIR):
    source: str
    target: str
    relation: str