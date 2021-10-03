from pydantic import BaseModel

class ReplyRequest(BaseModel):
    recipe_id: str
    user_id: str
    comment_id: str
    body: str
    likes: list = []
    likes_count: int = 0
    replies_count: int = 0
    is_comment_reply: bool = True
    