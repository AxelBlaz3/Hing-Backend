from pydantic import BaseModel

class ChangePasswordRequest(BaseModel):
    password: str
    user_id:str