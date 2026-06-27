from pydantic import BaseModel
from uuid import uuid4

class BaseIR(BaseModel):
    id: str = uuid4().hex