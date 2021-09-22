from pydantic import BaseModel

class RecipeRequest(BaseModel):
    user_id: str
    title: str
    description: str
    category: int
    likes: list = []
    favorites: list = []
    ingredients: str
    likes_count: int = 0
    comments_count: int = 0