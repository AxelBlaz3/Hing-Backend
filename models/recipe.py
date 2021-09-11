from typing import List, Optional
from pydantic import BaseModel
from werkzeug.datastructures import FileStorage


class Ingredient(BaseModel):    
    name: str
    qty: int


class Recipe(BaseModel):
    user_id: str
    title: str
    sub_title: str
    description: str
    category: str
    is_image: bool
    is_video: bool
    ingredients: List[Ingredient]   