from pydantic import BaseModel


class ReportRecipeRequest(BaseModel):
    user_id: str
    report_reason = str
    recipe_id = str
