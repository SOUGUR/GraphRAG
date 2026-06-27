from app.models.ir.base_ir import BaseIR

class ProjectIR(BaseIR):
    name: str
    root_path: str