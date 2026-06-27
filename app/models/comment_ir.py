from app.models.ir.base_ir import BaseIR

class CommentIR(BaseIR):
    text: str
    lineno: int