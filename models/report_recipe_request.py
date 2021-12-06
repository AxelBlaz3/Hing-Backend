from pydantic import BaseModel

class ReportedRecipeRequest(BaseModel):
    user_id: str
    report_reason=str
    recipe_id=str