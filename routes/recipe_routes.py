from models.recipe import Recipe
from repository.recipe_repository import RecipeRepository
from routes import recipe_api
from constants import RECIPE_ENDPOINT
from pydantic.error_wrappers import ValidationError
from models.response import Response
from flask import jsonify, request, json
from bson import json_util

@recipe_api.post(RECIPE_ENDPOINT)
def new_recipe():
    try:
        recipe_request = Recipe(**request.form.to_dict())

        if recipe_request.is_image and not request.files.get('image', None):
            return Response(status=False, msg='Image not uploaded', status_code=400), 400 

        if recipe_request.is_video and not request.files.get('video', None):
            return Response(status=False, msg='Video not uploaded', status_code=400), 400 

        result = RecipeRepository.create_recipe(recipe_request)

        if isinstance(result, dict):
            return jsonify(json.loads(json_util.dumps(result)))
        else:
            return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        return Response(status=False, msg='Some error occured', status_code=400), 400    