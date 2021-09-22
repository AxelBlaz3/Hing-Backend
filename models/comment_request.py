from pydantic import BaseModel

class CommentRequest(BaseModel):
    recipe_id: str
    user_id: str
    body: str
    likes: list = []
    likes_count: int = 0
    replies_count: int = 0
    