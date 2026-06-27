from app.models.ir.base_ir import BaseIR

class FileIR(BaseIR):
    name: str
    path: str
    extension: str
    size: int
    lines_of_code: int
    sha256: str
    module: str
    source_code: str = "" 