from typing import Optional
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage

class EditProfileRequest(BaseModel):
    user_id: str
    email: str
    display_name: str
    image: Optional[FileStorage] = None

    class Config:
        arbitrary_types_allowed = True