from pydantic import BaseModel

class LikeRequest(BaseModel):
    recipe_id: str
    user_id: str