from pydantic import BaseModel

class SignupRequest(BaseModel):
    display_name: str
    email: str
    password: str
    followers: list = []
    following: list = []