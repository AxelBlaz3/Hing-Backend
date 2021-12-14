from pydantic import BaseModel

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    user_id:str