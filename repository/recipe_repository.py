from flask.typing import StatusCode
from flask_pymongo import PyMongo
import pymongo
from pymongo.command_cursor import CommandCursor
from pymongo.message import update
from werkzeug.exceptions import NotFound
from models.like_request import LikeRequest
from pymongo.collection import ReturnDocument
from pymongo.results import InsertOneResult
from models.report_recipe_request import ReportRecipeRequest
from models.response import Response
from typing import List
from repository import uploads, mongo
from constants import COMMENTS_COLLECTION, NOTIFICATIONS_COLLECTION, RECIPES_COLLECTION, MEDIA_COLLECTION, REPORTED_RECIPES_COLLECTION, USER_INGREDIENTS_COLLECTION, USERS_COLLECTION
from extensions import MediaType, NotificationType
from flask import json, request
from bson import ObjectId, json_util
from datetime import datetime
from common.firebase_utils import FirebaseUtils


class RecipeRepository:
    @classmethod
    def create_recipe(*args) -> Response:
        try:
            _, upload_folder, files, recipe_request = args

            if not files:
                return Response(status=False, msg='No media uploaded', status_code=400)

            recipe_request.ingredients = json.loads(recipe_request.ingredients)
            recipe_request.user_id = ObjectId(recipe_request.user_id)

            recipe_dict = recipe_request.dict()
            recipe_dict['created_at'] = datetime.utcnow()
            insert_result: InsertOneResult = mongo.db[RECIPES_COLLECTION].insert_one(
                recipe_dict)

            # Upload media
            media: List[str] = []

            for file in files.to_dict().values():
                media_type = MediaType.VIDEO if file.filename.rsplit(
                    '.', 1)[1].lower() in uploads.VIDEO_EXTENSIONS else MediaType.IMAGE
                upload_type = 'videos' if media_type == MediaType.VIDEO else 'images'
                saved_path = uploads.upload_file(upload_folder=upload_folder, upload_type=upload_type, _id=str(
                    insert_result.inserted_id), file=file)
                media.append({
                    'media_path': saved_path,
                    'media_type': media_type,
                    'recipe_id': insert_result.inserted_id
                })

            mongo.db[MEDIA_COLLECTION].insert_many(media)

            # notification: dict = {
            #             'created_at': datetime.utcnow(),
            #             'other_user_id': ObjectId(recipe_request.user_id),
            #             'recipe_id': insert_result.inserted_id,
            #             'type': NotificationType.NEW_POST
            #         }
            # mongo.db[NOTIFICATIONS_COLLECTION].insert_one(document=notification)

            return Response(status=True, msg='New recipe added', status_code=201)
        except Exception as e:
            print(e)
            return Response(status=False, msg='Something went wrong', status_code=400)

    @staticmethod
    def like_recipe(like_request: LikeRequest) -> Response:
        try:
            recipe_id = ObjectId(like_request.recipe_id)
            user_id = ObjectId(like_request.user_id)
            filter = {'_id': recipe_id}

            update = {
                '$addToSet': {
                    'likes': user_id
                }
            }
            updated_recipe = mongo.db[RECIPES_COLLECTION].find_one_and_update(
                filter=filter, update=update, return_document=ReturnDocument.AFTER)

            if not updated_recipe:
                return Response(status=False, msg='Recipe not found', status_code=404)

            if user_id != updated_recipe['user_id']:
                notification: dict = {
                    'created_at': datetime.utcnow(),
                    'user_id': ObjectId(updated_recipe['user_id']),
                    'other_user_id': ObjectId(like_request.user_id),
                    'recipe_id': updated_recipe['_id'],
                    'type': NotificationType.LIKE_POST
                }
                mongo.db[NOTIFICATIONS_COLLECTION].insert_one(
                    document=notification)

                user = mongo.db[USERS_COLLECTION].find_one_or_404(
                    {'_id': ObjectId(updated_recipe['user_id'])}, {'firebase_token': 1})
                user_who_liked = mongo.db[USERS_COLLECTION].find_one_or_404(
                    {'_id': user_id}, {'display_name': 1})

                if 'firebase_token' in user and user['firebase_token']:
                    FirebaseUtils.send_notification(token=user['firebase_token'], image=None, notification_data={
                                                    'display_name': user_who_liked['display_name'], 'type': f'{NotificationType.LIKE_POST}', 'recipe': updated_recipe['title']})

            return Response(status=True, msg='Likes updated', status_code=200)
        except NotFound:
            return Response(status=False, msg='Recipe not found', status_code=404)
        except Exception as e:
            return Response(status=False, msg='Something went wrong', status_code=400)

    @staticmethod
    def unlike_recipe(like_request: LikeRequest) -> Response:
        try:
            recipe_id = ObjectId(like_request.recipe_id)
            user_id = ObjectId(like_request.user_id)

            filter = {'_id': ObjectId(like_request.recipe_id)}

            mongo.db[RECIPES_COLLECTION].find_one_or_404(filter, {'_id': 1})
            recipe_likes = mongo.db[RECIPES_COLLECTION].find_one(
                {'_id': recipe_id, 'likes': user_id}, {'_id': 1})

            if recipe_likes:
                update = {
                    '$pull': {
                        'likes': ObjectId(like_request.user_id)
                    },
                    '$inc': {
                        'likes_count': -1
                    }
                }

                updated_recipe = mongo.db[RECIPES_COLLECTION].find_one_and_update(
                    filter=filter, update=update, return_document=ReturnDocument.AFTER)

                if not updated_recipe:
                    return Response(status=False, msg='Recipe not found', status_code=404)

            return Response(status=True, msg='Likes updated', status_code=200)
        except NotFound:
            return Response(status=False, msg='Recipe not found', status_code=404)
        except Exception as e:
            return Response(status=False, msg='Something went wrong', status_code=400)

    @staticmethod
    def add_to_favorites(like_request: LikeRequest) -> Response:
        try:
            filter = {'_id': ObjectId(like_request.recipe_id)}
            update = {'$addToSet': {
                'favorites': ObjectId(like_request.user_id)
            }}
            updated_user = mongo.db[RECIPES_COLLECTION].find_one_and_update(
                filter=filter, update=update, return_document=ReturnDocument.AFTER)

            if not updated_user:
                return Response(status=False, msg='User not found', status_code=404)

            return Response(status=True, msg='Favorites updated', status_code=200)
        except Exception as e:
            print(e)

    @staticmethod
    def remove_from_favorites(like_request: LikeRequest) -> Response:
        try:
            filter = {'_id': ObjectId(like_request.recipe_id)}
            update = {'$pull': {
                'favorites': ObjectId(like_request.user_id)
            }}
            updated_user = mongo.db[RECIPES_COLLECTION].find_one_and_update(
                filter=filter, update=update, return_document=ReturnDocument.AFTER)

            if not updated_user:
                return Response(status=False, msg='User not found', status_code=404)

            return Response(status=True, msg='Favorites updated', status_code=200)
        except Exception as e:
            print(e)

    @staticmethod
    def get_recipe(recipe_id: str, user_id: str):
        try:
            if not recipe_id:
                return Response(status=False, msg='Invalid recipe id', status_code=400)

            # if not user_id:
            #     return Response(status=False, msg='Invalid user id', status_code=400)

            try:
                recipe_id = ObjectId(recipe_id)

                if user_id:
                    user_id = ObjectId(user_id)
            except:
                return Response(status=False, msg='Invalid object id', status_code=400)

            recipe = mongo.db[RECIPES_COLLECTION].aggregate([
                {
                    '$match': {
                        '_id': recipe_id
                    }
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
                    '$lookup': {
                        'from': COMMENTS_COLLECTION,
                        'localField': '_id',
                        'foreignField': 'recipe_id',
                        'as': 'comments'
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
                        'likes_count': {
                            '$size': '$likes'
                        },
                        'likes': 1,
                        'favorites': 1,
                        'comments_count': {
                            '$size': '$comments'
                        }
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
                    '$addFields': {
                        'user.followers_count': {
                            '$size': '$user.followers'
                        }
                    }
                },
                {
                    '$addFields': {
                        'user.following_count': {
                            '$size': '$user.following'
                        }
                    }
                },
                {
                    '$lookup': {
                        'from': RECIPES_COLLECTION,
                        'as': 'posts',
                        'localField': 'user._id',
                        'foreignField': 'user_id'
                    }
                },
                {
                    '$addFields': {
                        'user.posts_count': {
                            '$size': '$posts'
                        }
                    }
                },
                {
                    '$project': {
                        'posts': 0
                    }
                },
                {
                    '$project': {
                        'user.password': 0,
                        'likes': 0
                    }
                }])

            return recipe
        except Exception as e:
            print(e)

    @staticmethod
    def get_who_liked(recipe_id: str, user_id: str, page: int = 1, per_page: int = 10):
        try:
            recipe_id = ObjectId(recipe_id)
            user_id = ObjectId(user_id)
            likes = mongo.db[RECIPES_COLLECTION].aggregate([
                {
                    '$match': {
                        '_id': recipe_id
                    }
                },
                {
                    '$skip': 0 if page <= 1 else per_page * (page - 1)
                },
                {
                    '$limit': per_page
                },
                {
                    '$project': {
                        '_id': 0,
                        'likes': 1
                    }
                },
                {
                    '$lookup': {
                        'from': 'users',
                        'as': 'users',
                        'let': {
                            'likes': '$likes'
                        },
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$in': [
                                            '$_id', '$$likes'
                                        ]
                                    }
                                }
                            },
                            {
                                '$addFields': {
                                    'is_following': {
                                        '$in': [user_id, '$followers']
                                    }
                                }
                            },
                            {
                                '$project': {
                                    '_id': 1,
                                    'display_name': 1,
                                    'image': 1,
                                    'is_following': 1
                                }
                            }
                        ]
                    }
                },
                {
                    '$project': {
                        'likes': 0
                    }
                }
            ])
            return likes.next()['users']
        except Exception as e:
            return []

    @staticmethod
    def search_recipes(query: str, user_id: str, page: int = 1, per_page: int = 10):
        try:
            user_id = ObjectId(user_id)
            recipes: CommandCursor = mongo.db[RECIPES_COLLECTION].aggregate([
                {
                    '$match': {
                        '$expr': {
                            '$and': [
                                {
                                '$regexMatch': {'input': '$title', 'regex': f'{query}.*', 'options': 'i'}},
                                {'$not': {'$in': [user_id, '$reported_users']}}
                            ]
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
                    '$lookup': {
                        'from': COMMENTS_COLLECTION,
                        'localField': '_id',
                        'foreignField': 'recipe_id',
                        'as': 'comments'
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
                        'likes_count': {
                            '$size': '$likes'
                        },
                        'likes': 1,
                        'favorites': 1,
                        'comments_count': {
                            '$size': '$comments'
                        }
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
                    '$lookup': {
                        'from': USER_INGREDIENTS_COLLECTION,
                        'as': 'my_ingredients',
                        'let': {
                            'recipeId': '$_id'
                        },
                        'pipeline': [
                            {
                                '$match': {
                                    '$expr': {
                                        '$and': [
                                            {'$eq': ['$user_id', user_id]},
                                            {'$eq': [
                                                '$recipe_id', '$$recipeId']}
                                        ]
                                    }
                                }
                            },
                            {
                                '$limit': 1
                            },
                            {
                                '$project': {
                                    'ingredients': 1,
                                    '_id': 0
                                }
                            }
                        ]
                    }
                },
                # {
                #     '$addFields': {
                #         'my_ingredients': {
                #             '$getField': {
                #                 'field': 'ingredients',
                #                 'input': {
                #                     '$arrayElemAt': [
                #                         '$my_ingredients', 0
                #                     ]
                #                 }
                #             }
                #         }
                #     }
                # },
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

    # report recipe
    @staticmethod
    def report_recipe(report_recipe_request: ReportRecipeRequest):
        try:
            report_data_dict = report_recipe_request.dict()

            report_data_dict['user_id'] = ObjectId(
                report_recipe_request.user_id)
            report_data_dict['recipe_id'] = ObjectId(
                report_recipe_request.recipe_id)

            mongo.db[RECIPES_COLLECTION].find_one_and_update(filter={'_id': report_data_dict['recipe_id']}, update={
                '$push': {'reported_users': report_data_dict['user_id']}
            }, return_document=ReturnDocument.AFTER)
            mongo.db[REPORTED_RECIPES_COLLECTION].insert_one(
                document=report_data_dict)

            return Response(status=True, msg='Recipe reported successfully!', status_code=200)
        except Exception as e:
            print(e)
            return Response(status=False, msg='Something went wrong', status_code=400)
