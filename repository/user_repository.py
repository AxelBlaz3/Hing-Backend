from bson.objectid import ObjectId
from pymongo.command_cursor import CommandCursor
from constants import USERS_COLLECTION
from models.response import Response
from typing import Union
from repository import mongo, bcrypt
from werkzeug.exceptions import NotFound
from pymongo.errors import DuplicateKeyError
from flask_jwt_extended import create_access_token


class UserRepository:
    @classmethod
    def login(*args) -> Union[dict, Response]:
        _, login_request = args
        filter = {'email': login_request.email}
        try:
            user = mongo.db[USERS_COLLECTION].find_one_or_404(
                filter)
            if user:
                if bcrypt.check_password_hash(user['password'], login_request.password):
                    del user['password']
                    user['access_token'] = create_access_token(identity=str(user['_id']))
                    return user
                else:
                    return Response(status_code=403, msg='Incorrect password', status=False)
        except NotFound:
            return Response(status_code=404, msg='No user found', status=False)
        except Exception:
            return Response(status_code=400, msg='Some error occured', status=False)

    @staticmethod
    def signup(signup_request) -> Union[dict, Response]:
        mongo.db[USERS_COLLECTION].create_index('email', unique=True)

        signup_data = signup_request.dict()
        signup_data['image'] = None

        signup_data['password'] = bcrypt.generate_password_hash(
            password=signup_data['password'])

        try:
            insert_result = mongo.db[USERS_COLLECTION].insert_one(signup_data)
            filter = {'_id': insert_result.inserted_id}
            user = mongo.db[USERS_COLLECTION].find_one(filter, {'password': 0})
            return user
        except DuplicateKeyError as e:
            return Response(status_code=409, msg='Not available', field=list(e.details['keyValue'].keys())[0], status=False)
        except Exception as e:
            print(e)
            return Response(status_code=400, msg='Some error occured', status=False)


    @staticmethod
    def get_followers(user_id) -> Union[CommandCursor, Response]:
        try:
            if user_id is None:
                return Response(status=True, status_code=400, msg='Invalid user id')

            followers = mongo.db[USERS_COLLECTION].aggregate([
                {
                    '$match': {
                        '_id': ObjectId(user_id)
                    }
                }, 
                {
                    '$project': {
                        '_id': 0,
                        'followers': 1
                    }
                }, 
                {
                    '$lookup': {
                        'from': 'users',
                        'localField': 'followers',
                        'foreignField': '_id',
                        'as': 'followers'
                    }
                },
                {
                    '$project': {
                        'user.password': 0
                    }
                }
            ])
            return followers
        except:
            return []

    @staticmethod
    def get_following(user_id) -> Union[CommandCursor, Response]:
        try:
            if user_id is None:
                return Response(status=True, status_code=400, msg='Invalid user id')

            followers = mongo.db[USERS_COLLECTION].aggregate([
                {
                    '$match': {
                        '_id': ObjectId(user_id)
                    }
                }, 
                {
                    '$project': {
                        '_id': 0,
                        'following': 1
                    }
                }, 
                {
                    '$lookup': {
                        'from': 'users',
                        'localField': 'following',
                        'foreignField': '_id',
                        'as': 'followers'
                    }
                },
                {
                    '$project': {
                        'user.password': 0
                    }
                }
            ])
            return followers
        except:
            return []                