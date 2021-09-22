from models.like_request import LikeRequest
from models.recipe_request import RecipeRequest
from repository.recipe_repository import RecipeRepository
from routes import recipe_api
from constants import ADD_TO_FAVORITES_ENDPOINT, LIKE_RECIPE_ENDPOINT, NEW_RECIPE_ENDPOINT, REMOVE_FROM_FAVORITES_ENDPOINT, UNLIKE_RECIPE_ENDPOINT
from pydantic.error_wrappers import ValidationError
from models.response import Response
from flask import jsonify, request, json, current_app
from bson import json_util

@recipe_api.post(NEW_RECIPE_ENDPOINT)
def new_recipe():
    try:
        recipe_request = RecipeRequest(**request.form.to_dict())

        result = RecipeRepository.create_recipe(current_app.config['UPLOAD_FOLDER'], request.files, recipe_request)

        return result.dict(), result.status_code
    except ValidationError as e:
        print(e)
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400    

@recipe_api.put(LIKE_RECIPE_ENDPOINT)
def like_recipe():
    try:
        like_request = LikeRequest(**request.json)

        result = RecipeRepository.like_recipe(like_request=like_request)

        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400 


@recipe_api.put(UNLIKE_RECIPE_ENDPOINT)
def unlike_recipe():
    try:
        like_request = LikeRequest(**request.json)

        result = RecipeRepository.unlike_recipe(like_request=like_request)

        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400 



@recipe_api.put(ADD_TO_FAVORITES_ENDPOINT)
def favorite_recipe():
    try:
        like_request = LikeRequest(**request.json)

        result = RecipeRepository.add_to_favorites(like_request=like_request)

        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@recipe_api.put(REMOVE_FROM_FAVORITES_ENDPOINT)
def unfavorite_recipe():
    try:
        like_request = LikeRequest(**request.json)

        result = RecipeRepository.remove_from_favorites(like_request=like_request)

        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400                         
