from pydantic import BaseModel

class BlockRequest(BaseModel):
    user_id: str
    other_user_id: str