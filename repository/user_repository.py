from pymongo.results import UpdateResult
from models.follow_request import FollowRequest
from bson.objectid import ObjectId
import pymongo
from pymongo.command_cursor import CommandCursor
from constants import RECIPES_COLLECTION, USERS_COLLECTION
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
                    user['access_token'] = create_access_token(
                        identity=str(user['_id']))
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
    def get_followers(user_id, page=1, per_page=10) -> Union[CommandCursor, Response]:
        try:
            if user_id is None:
                return Response(status=True, status_code=400, msg='Invalid user id')

            user_id = ObjectId(user_id)

            followers: CommandCursor = mongo.db[USERS_COLLECTION].aggregate([
                {
                    '$match': {
                        '_id': user_id
                    }
                }, {
                    '$project': {
                        'followers': 1,
                        'following': 1
                    }
                }, {
                    '$lookup': {
                        'from': 'users',
                        'as': 'users',
                        'let': {
                            'followers': '$followers',
                            'following': '$following'
                        },
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$in': [
                                            '$_id', '$$followers'
                                        ]
                                    }
                                }
                            }, {
                                '$project': {
                                    'display_name': 1,
                                    'image': 1
                                }
                            }, {
                                '$addFields': {
                                    'is_following': {
                                        '$in': [
                                            '$_id', '$$following'
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }, {
                    '$project': {
                        'followers': 0,
                        'following': 0,
                        '_id': 0,
                    }
                }
            ])
            return followers.next()['users']
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def get_following(user_id, other_user_id = None, page=1, per_page=10) -> Union[CommandCursor, Response]:
        try:
            if user_id is None:
                return Response(status=True, status_code=400, msg='Invalid user id')

            user_id = ObjectId(user_id)    

            if other_user_id:
                other_user_id = ObjectId(other_user_id)

            following: CommandCursor = mongo.db[USERS_COLLECTION].aggregate([
                {
                    '$match': {
                        '_id': user_id
                    }
                }, {
                    '$project': {
                        'following': 1
                    }
                }, {
                    '$lookup': {
                        'from': 'users',
                        'as': 'users',
                        'let': {
                            'following': '$following'
                        },
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$in': [
                                            '$_id', '$$following'
                                        ]
                                    }
                                }
                            }, {
                                '$project': {
                                    'display_name': 1,
                                    'image': 1
                                }
                            }, {
                                '$addFields': {
                                    'is_following': {
                                        '$in': [other_user_id if other_user_id else user_id, ]
                                    }
                                }
                            }
                        ]
                    }
                }, {
                    '$project': {
                        'following': 0,
                        '_id': 0,
                    }
                }
            ])
            return following.next()['users']
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def get_posts(user_id, page=1, per_page=10):
        try:
            user_id = ObjectId(user_id)
            recipes = mongo.db[RECIPES_COLLECTION].aggregate([
                {
                    '$match': {
                        '$expr': {
                            '$eq': ['$user_id', user_id]
                        }
                    }
                },
                {
                    '$sort': {
                        'created_at': pymongo.DESCENDING
                    }
                },
                {
                    '$skip': 0 if page <= 1 else per_page * (page - 1)
                },
                {
                    '$limit': per_page
                },
                {
                    '$lookup': {
                        'from': 'media',
                        'localField': '_id',
                        'foreignField': 'recipe_id',
                        'as': 'media'
                    }
                },
                {
                    '$lookup': {
                        'from': 'users',
                        'localField': 'user_id',
                        'foreignField': '_id',
                        'as': 'user'
                    }
                },
                {
                    '$project': {
                        'user': {
                            '$arrayElemAt': [
                                '$user', 0
                            ]
                        },
                        'description': 1,
                        'ingredients': 1,
                        'category': 1,
                        'media': 1,
                        'title': 1,
                        'likes_count': 1,
                        'likes': 1,
                        'favorites': 1,
                        'comments_count': 1
                    }
                },
                {
                    '$addFields': {
                        'is_favorite': {
                            '$in': [user_id, '$favorites']
                        }
                    }
                },
                {
                    '$addFields': {'user.is_following': {
                        '$in': [user_id, '$user.followers']
                    }
                    }
                },
                {
                    '$addFields': {'is_liked': {
                        '$in': [user_id, '$likes']
                    }
                    }
                },
                {
                    '$project': {
                        'user.password': 0,
                        'user.email': 0,
                        'user.followers': 0,
                        'user.following': 0,
                        'likes': 0
                    }
                }
            ])
            return recipes
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def get_favorites(user_id, page=1, per_page=10):
        try:
            user_id = ObjectId(user_id)
            recipes: CommandCursor = mongo.db[RECIPES_COLLECTION].aggregate([
                {
                    '$match': {
                        '$expr': {
                            '$in': [user_id, '$favorites']
                        }
                    }
                },
                {
                    '$sort': {
                        'created_at': pymongo.DESCENDING
                    }
                },
                {
                    '$skip': 0 if page <= 1 else per_page * (page - 1)
                },
                {
                    '$limit': per_page
                },
                {
                    '$lookup': {
                        'from': 'media',
                        'localField': '_id',
                        'foreignField': 'recipe_id',
                        'as': 'media'
                    }
                },
                {
                    '$lookup': {
                        'from': 'users',
                        'localField': 'user_id',
                        'foreignField': '_id',
                        'as': 'user'
                    }
                },
                {
                    '$project': {
                        'user': {
                            '$arrayElemAt': [
                                '$user', 0
                            ]
                        },
                        'description': 1,
                        'ingredients': 1,
                        'category': 1,
                        'media': 1,
                        'title': 1,
                        'likes_count': 1,
                        'likes': 1,
                        'favorites': 1,
                        'comments_count': 1
                    }
                },
                {
                    '$addFields': {
                        'is_favorite': {
                            '$in': [user_id, '$favorites']
                        }
                    }
                },
                {
                    '$addFields': {'user.is_following': {
                        '$in': [user_id, '$user.followers']
                    }
                    }
                },
                {
                    '$addFields': {'is_liked': {
                        '$in': [user_id, '$likes']
                    }
                    }
                },
                {
                    '$project': {
                        'user.password': 0,
                        'user.email': 0,
                        'user.followers': 0,
                        'user.following': 0,
                        'likes': 0
                    }
                }
            ])
            return recipes
        except:
            return []

    @staticmethod
    def follow_user(follow_request: FollowRequest):
        try:
            followee_id = ObjectId(follow_request.followee_id)
            follower_id = ObjectId(follow_request.follower_id)

            mongo.db[USERS_COLLECTION].update_one(filter={'_id': followee_id}, update={
                                                  '$addToSet': {'followers': follower_id}})
            mongo.db[USERS_COLLECTION].update_one(filter={'_id': follower_id}, update={
                                                  '$addToSet': {'following': followee_id}})

            return Response(status=True, msg='Followers updated', status_code=200)
        except:
            pass

        return Response(status=False, msg='Something went wrong', status_code=400)

    @staticmethod
    def unfollow_user(follow_request: FollowRequest):
        try:
            followee_id = ObjectId(follow_request.followee_id)
            follower_id = ObjectId(follow_request.follower_id)

            mongo.db[USERS_COLLECTION].update_one(filter={'_id': followee_id}, update={
                                                  '$pull': {'followers': follower_id}})
            mongo.db[USERS_COLLECTION].update_one(filter={'_id': follower_id}, update={
                                                  '$pull': {'following': followee_id}})

            return Response(status=True, msg='Followers updated', status_code=200)
        except:
            pass

        return Response(status=False, msg='Something went wrong', status_code=400)
