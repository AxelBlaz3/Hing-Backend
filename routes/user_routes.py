from models.response import Response
from flask import json
from bson import json_util
from flask.json import jsonify
from routes import user_api
from constants import SIGNUP_ENDPOINT, LOGIN_ENDPOINT
from models.signup_request import SignupRequest
from models.login_request import LoginRequest
from pydantic.error_wrappers import ValidationError
from flask import request
from repository.user_repository import UserRepository
from flask_pydantic import validate

@user_api.post(SIGNUP_ENDPOINT)
@validate()
def signup():
    try:
        signup_request = SignupRequest(**request.json)
        result = UserRepository.signup(signup_request)

        if isinstance(result, dict):
            return jsonify(json.loads(json_util.dumps(result)))
        else:
            return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        return Response(status=False, msg='Some error occured', status_code=400), 400    

@user_api.post(LOGIN_ENDPOINT)
@validate()
def login_user():
    try:
        login_request = LoginRequest(**request.json)
    except ValidationError as e:
        return e.json(), 400

    result = UserRepository.login(login_request)
    if isinstance(result, dict):
        return jsonify(json.loads(json_util.dumps(result)))
    else:
        return result.dict(), result.status_code
