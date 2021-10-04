from models.create_password_request import CreatePasswordRequest
from models.edit_profile_request import EditProfileRequest
from models.follow_request import FollowRequest
from bson.objectid import ObjectId
from pymongo.command_cursor import CommandCursor
from models.response import Response
from flask import json
from bson import json_util
from flask.json import jsonify
from routes import user_api
from constants import CREATE_NEW_PASSWORD_ENDPOINT, EDIT_PROFILE_ENDPOINT, FOLLOW_USER_ENDPOINT, GET_FOLLOWERS_ENDPOINT, GET_FOLLOWING_ENDPOINT, GET_NOTIFICATIONS_ENDPOINT, GET_USER_FAVORITES_ENDPOINT, GET_USER_POSTS_ENDPOINT, SEND_RESET_CODE_ENDPOINT, SIGNUP_ENDPOINT, LOGIN_ENDPOINT, UNFOLLOW_USER_ENDPOINT, UPDATE_FIREBASE_TOKEN_ENDPOINT
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
            return jsonify(json.loads(json_util.dumps(result))), 201
        else:
            return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
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


@user_api.put(FOLLOW_USER_ENDPOINT)
@validate()
def follow_user():
    try:
        follow_request = FollowRequest(**request.json)
    except ValidationError as e:
        return e.json(), 400

    result = UserRepository.follow_user(follow_request=follow_request)
    
    return result.dict(), result.status_code


@user_api.put(UNFOLLOW_USER_ENDPOINT)
@validate()
def unfollow_user():
    try:
        follow_request = FollowRequest(**request.json)
    except ValidationError as e:
        return e.json(), 400

    result = UserRepository.unfollow_user(follow_request=follow_request)

    return result.dict(), result.status_code


@user_api.get(GET_FOLLOWERS_ENDPOINT)
def get_followers(user_id):
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        other_user_id = request.args.get('other_user_id', default=None)

        result = UserRepository.get_followers(user_id=user_id, other_user_id=other_user_id, page=page, per_page=per_page)
        if isinstance(result, list):
            return jsonify(json.loads(json_util.dumps(result)))
        else:
            return result.dict(), result.status_code
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400  


@user_api.get(GET_FOLLOWING_ENDPOINT)
def get_following(user_id):
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        other_user_id = request.args.get('other_user_id', default=None)

        result = UserRepository.get_following(user_id=user_id, other_user_id=other_user_id, page=page, per_page=per_page)
        if isinstance(result, list):
            return jsonify(json.loads(json_util.dumps(result)))
        else:
            return result.dict(), result.status_code
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400        


@user_api.get(GET_USER_POSTS_ENDPOINT)
def get_posts(user_id):
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        other_user_id = request.args.get('other_user_id', default=None, type=str)

        result = UserRepository.get_posts(user_id=user_id, other_user_id=other_user_id, page=page, per_page=per_page)
        if isinstance(result, CommandCursor):
            return jsonify(json.loads(json_util.dumps(result)))
        else:
            return result.dict(), result.status_code
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@user_api.get(GET_USER_FAVORITES_ENDPOINT)
def get_favorites(user_id):
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        result = UserRepository.get_favorites(user_id=user_id, page=page, per_page=per_page)
        if isinstance(result, CommandCursor):
            return jsonify(json.loads(json_util.dumps(result)))
        else:
            return result.dict(), result.status_code
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@user_api.get(GET_NOTIFICATIONS_ENDPOINT)
def get_notifications(user_id):
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        result = UserRepository.get_notifications(user_id=user_id, page=page, per_page=per_page)
        if isinstance(result, CommandCursor):
            return jsonify(json.loads(json_util.dumps(result)))
        else:
            return result.dict(), result.status_code
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400              


@user_api.put(EDIT_PROFILE_ENDPOINT)
@validate()
def edit_profile():
    try:
        edit_profile_request = EditProfileRequest(**request.form.to_dict(), **request.files)
    except ValidationError as e:
        return e.json(), 400

    result = UserRepository.update_user(edit_profile_request=edit_profile_request, image=request.files.get('image'))
    
    return result.dict(), result.status_code


@user_api.put(UPDATE_FIREBASE_TOKEN_ENDPOINT)
def update_firebase_token():
    payload = request.json
    result = UserRepository.update_firebase_token(payload=payload)
    return result.dict(), result.status_code


@user_api.put(CREATE_NEW_PASSWORD_ENDPOINT)
@validate()
def create_new_password():
    try:
        create_password_request = CreatePasswordRequest(**request.json)
    except ValidationError as e:
        return e.json(), 400

    result = UserRepository.create_new_password(create_password_request=create_password_request)
    
    return result.dict(), result.status_code   


@user_api.post(SEND_RESET_CODE_ENDPOINT)
def send_reset_code():
    payload = request.json
    email = payload['email'] if 'email' in payload else None
    result = UserRepository.send_verification_code(email=email)

    return result.dict(), result.status_code
