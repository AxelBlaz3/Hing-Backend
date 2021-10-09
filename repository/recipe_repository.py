from werkzeug.exceptions import NotFound
from pymongo.message import update
from models.like_request import LikeRequest
from pymongo.collection import ReturnDocument
from pymongo.results import InsertOneResult
from models.response import Response
from typing import List
from repository import uploads, mongo
from constants import NOTIFICATIONS_COLLECTION, RECIPES_COLLECTION, MEDIA_COLLECTION, REPLIES_COLLECTION, USERS_COLLECTION
from extensions import MediaType, NotificationType
from flask import json
from bson import ObjectId
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
            insert_result: InsertOneResult = mongo.db[RECIPES_COLLECTION].insert_one(recipe_dict
            )

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
                mongo.db[NOTIFICATIONS_COLLECTION].insert_one(document=notification)

                user = mongo.db[USERS_COLLECTION].find_one_or_404({'_id': ObjectId(updated_recipe['user_id'])}, {'firebase_token': 1})
                user_who_liked = mongo.db[USERS_COLLECTION].find_one_or_404({'_id': user_id}, {'display_name': 1})

                if 'firebase_token' in user and user['firebase_token']:
                    FirebaseUtils.send_notification(token=user['firebase_token'], image=None, notification_data={'display_name': user_who_liked['display_name'], 'type': f'{NotificationType.LIKE_POST}', 'recipe': updated_recipe['title']})
            
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
            recipe_likes = mongo.db[RECIPES_COLLECTION].find_one({'_id': recipe_id, 'likes': user_id}, {'_id': 1})

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
