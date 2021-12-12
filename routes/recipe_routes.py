from models.like_request import LikeRequest
from models.recipe_request import RecipeRequest
from models.report_recipe_request import ReportRecipeRequest
from repository.recipe_repository import RecipeRepository
from routes import recipe_api
from constants import ADD_TO_FAVORITES_ENDPOINT, GET_RECIPE_ENDPOINT, GET_RECIPE_LIKES_ENDPOINT, GET_REPORT_RECIPE_ENDPOINT, LIKE_RECIPE_ENDPOINT, NEW_RECIPE_ENDPOINT, REMOVE_FROM_FAVORITES_ENDPOINT, REPORT_RECIPE_ENDPOINT, SEARCH_RECIPES_ENDPOINT, UNLIKE_RECIPE_ENDPOINT
from pydantic.error_wrappers import ValidationError
from models.response import Response
from flask import jsonify, request, json, current_app
from bson import json_util


@recipe_api.post(NEW_RECIPE_ENDPOINT)
def new_recipe():
    try:
        recipe_request = RecipeRequest(**request.form.to_dict())

        result = RecipeRepository.create_recipe(
            current_app.config['UPLOAD_FOLDER'], request.files, recipe_request)

        return result.dict(), result.status_code
    except ValidationError as e:
        print(e)
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@recipe_api.get(GET_RECIPE_ENDPOINT)
def get_recipe():
    try:
        recipe_id = request.args.get('recipe_id')
        user_id = request.args.get('user_id')
        recipe = RecipeRepository.get_recipe(
            user_id=user_id, recipe_id=recipe_id)

        if not recipe:
            return {}

        return jsonify(json.loads(json_util.dumps(recipe.next())))
    except:
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

        result = RecipeRepository.remove_from_favorites(
            like_request=like_request)

        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@recipe_api.get(GET_RECIPE_LIKES_ENDPOINT)
def get_who_liked(recipe_id):
    try:
        page = request.args.get(key='page', default=1, type=int)
        user_id = request.args.get('user_id', default=None)
        result = RecipeRepository.get_who_liked(
            recipe_id=recipe_id, user_id=user_id, page=page)

        return jsonify(json.loads(json_util.dumps(result)))
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@recipe_api.get(SEARCH_RECIPES_ENDPOINT)
def searh_recipes(query):
    try:
        page = request.args.get(key='page', default=1, type=int)
        user_id = request.args.get('user_id', default=None)
        result = RecipeRepository.search_recipes(
            query=query, user_id=user_id, page=page)

        return jsonify(json.loads(json_util.dumps(result)))
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@recipe_api.post(REPORT_RECIPE_ENDPOINT)
def report_recipe():
    try:
        report_recipe_request = ReportRecipeRequest(**request.json)

        result = RecipeRepository.report_recipe(
            report_recipe_request=report_recipe_request)

        return result.to_dict, result.status_code
    except ValidationError as e:
        print(e)
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400
