from pydantic import BaseModel

class CommentLikeRequest(BaseModel):
    comment_id: str
    user_id: str

class ReplyLikeRequest(BaseModel):
    reply_id: str
    user_id: str