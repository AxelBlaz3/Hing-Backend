from pydantic import BaseModel

class FollowRequest(BaseModel):
    follower_id: str
    followee_id: str