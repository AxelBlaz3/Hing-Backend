from pydantic import BaseModel

class Response(BaseModel):
    status: bool
    msg: str
    status_code: int