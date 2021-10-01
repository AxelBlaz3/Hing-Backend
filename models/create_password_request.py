from pydantic import BaseModel

class CreatePasswordRequest(BaseModel):
    email: str
    password: str
    code: str