import os
from random import Random, random
from flask_mail import Message
from pymongo.collection import ReturnDocument

from pymongo.message import update
from pymongo.results import UpdateResult
from werkzeug.datastructures import FileStorage
from models.create_password_request import CreatePasswordRequest
from repository.uploads import upload_file
from models.edit_profile_request import EditProfileRequest
from datetime import datetime
from extensions import NotificationType
from models.follow_request import FollowRequest
from bson.objectid import ObjectId
import pymongo
from pymongo.command_cursor import CommandCursor
from constants import COMMENTS_COLLECTION, NOTIFICATIONS_COLLECTION, RECIPES_COLLECTION, REPLIES_COLLECTION, USERS_COLLECTION
from models.response import Response
from typing import Union
from repository import mongo, bcrypt
from werkzeug.exceptions import NotFound
from pymongo.errors import DuplicateKeyError
from flask import current_app, render_template
from flask_jwt_extended import create_access_token
from repository import mail
from common.push_notification import PushNotification


class UserRepository:
    @classmethod
    def login(*args) -> Union[dict, Response]:
        _, login_request = args
        filter = {'email': login_request.email}
        try:
            user = mongo.db[USERS_COLLECTION].find_one_or_404(
                filter, {'password': 1, '_id': 1})
            if user:
                if bcrypt.check_password_hash(user['password'], login_request.password):
                    del user['password']
                    user['access_token'] = create_access_token(
                        identity=str(user['_id']))

                    user = mongo.db[USERS_COLLECTION].aggregate([
                        {
                            '$match': {
                                '_id': user['_id']
                            }
                        },
                        {
                            '$addFields': {
                                'followers_count': {
                                    '$size': '$followers'
                                }
                            }
                        },
                        {
                            '$addFields': {
                                'following_count': {
                                    '$size': '$following'
                                }
                            }
                        },
                        {
                            '$project': {
                                'password': 0,
                                'following': 0
                            }
                        },
                        {
                            '$lookup': {
                                'from': RECIPES_COLLECTION,
                                'as': 'posts',
                                'localField': '_id',
                                'foreignField': 'user_id'
                            }
                        },
                        {
                            '$addFields': {
                                'posts_count': {
                                    '$size': '$posts'
                                }
                            }
                        },
                        {
                            '$project': {
                                'posts': 0
                            }
                        }
                    ])
                    return user.next()
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
    def send_verification_code(email: str) -> Response:
        try:
            if not email or len(email) == 0:
                return Response(status_code=400, msg='Invalid email', status=False)

            code = Random().randint(a=100000, b=999999)

            filter = {'email': email}
            update = {'$set': {
                'code': bcrypt.generate_password_hash(password=str(code))
            }}

            try:
                user = mongo.db[USERS_COLLECTION].find_one(filter=filter)
                mongo.db[USERS_COLLECTION].update_one(
                    filter=filter, update=update)
            except NotFound:
                return Response(status_code=404, msg='No account is associated with that email', status=False)

            message = Message(subject='Reset your password', recipients=[email], sender=current_app.config['MAIL_USERNAME'], html=render_template(
                'reset_password.html', name=user['display_name'], code=code))
            mail.send(message)
            return Response(status_code=200, msg='Mail sent', status=True)
        except Exception as e:
            print(f'{type(e)}: {e}')
            return Response(status_code=400, msg='Some error occured', status=False)

    @staticmethod
    def create_new_password(create_password_request: CreatePasswordRequest):
        try:
            filter = {'email': create_password_request.email}
            user = mongo.db[USERS_COLLECTION].find_one_or_404(filter=filter)

            if not bcrypt.check_password_hash(pw_hash=user['code'], password=create_password_request.code):
                return Response(status_code=403, msg='Invalid code', status=False)

            update_result: UpdateResult = mongo.db[USERS_COLLECTION].update_one(filter=filter, update={'$set': {
                'password': bcrypt.generate_password_hash(password=create_password_request.password)
            },
                '$unset': {
                'code': ''
            }})

            if update_result.modified_count > 0:
                return Response(status_code=200, msg='Password updated', status=True)

            return Response(status_code=400, msg='Something went wrong', status=False)

        except NotFound:
            return Response(status_code=404, msg='No account is associated with that email', status=False)
        except:
            return Response(status_code=400, msg='Something went wrong', status=False)

    @staticmethod
    def get_followers(user_id, other_user_id, page=1, per_page=10) -> Union[CommandCursor, Response]:
        try:
            if user_id is None:
                return Response(status=True, status_code=400, msg='Invalid user id')

            if other_user_id is None:
                return Response(status=True, status_code=400, msg='Invalid other user id')

            user_id = ObjectId(user_id)
            other_user_id = ObjectId(other_user_id)

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
                                    'image': 1,
                                    'followers': 1
                                }
                            }, {
                                '$addFields': {
                                    'is_following': {
                                        '$in': [other_user_id, '$followers']
                                    }
                                }
                            }, {
                                '$project': {
                                    'followers': 0
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
    def get_following(user_id, other_user_id, page=1, per_page=10) -> Union[CommandCursor, Response]:
        try:
            if user_id is None:
                return Response(status=True, status_code=400, msg='Invalid user id')

            if other_user_id is None:
                return Response(status=True, status_code=400, msg='Invalid other user id')

            user_id = ObjectId(user_id)
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
                                    'image': 1,
                                    'followers': 1
                                }
                            }, {
                                '$addFields': {
                                    'is_following': {
                                        '$in': [other_user_id, '$followers']
                                    }
                                }
                            }, {
                                '$project': {
                                    'followers': 0
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
    def get_posts(user_id, other_user_id, page=1, per_page=10):
        try:
            try:
                user_id = ObjectId(user_id)
                other_user_id = ObjectId(other_user_id)
            except:
                return Response(status_code=400, msg='Invalid id', status=False)

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
                            '$in': [other_user_id, '$favorites']
                        }
                    }
                },
                {
                    '$addFields': {'user.is_following': {
                        '$in': [other_user_id, '$user.followers']
                    }
                    }
                },
                {
                    '$addFields': {'is_liked': {
                        '$in': [other_user_id, '$likes']
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

            update_result = mongo.db[USERS_COLLECTION].update_one(filter={'_id': followee_id}, update={
                '$addToSet': {'followers': follower_id}})
            mongo.db[USERS_COLLECTION].update_one(filter={'_id': follower_id}, update={
                                                  '$addToSet': {'following': followee_id}})

            if update_result.modified_count > 0:
                # Send push notification to user for new follower.
                # Insert the notification in 'notifications' collection.

                notification: dict = {
                    'created_at': datetime.utcnow(),
                    'user_id': followee_id,
                    'other_user_id': follower_id,
                    'type': NotificationType.NEW_FOLLOWER
                }
                mongo.db[NOTIFICATIONS_COLLECTION].insert_one(
                    document=notification)

                user = mongo.db[USERS_COLLECTION].find_one_or_404({'_id': followee_id}, {'firebase_token': 1})
                user_who_followed = mongo.db[USERS_COLLECTION].find_one_or_404({'_id': follower_id}, {'display_name': 1})

                if 'firebase_token' in user and user['firebase_token']:
                    PushNotification.send_notification(token=user['firebase_token'], image=None, notification_data={'display_name': user_who_followed['display_name'], 'type': f'{NotificationType.NEW_FOLLOWER}'})

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

    @staticmethod
    def get_notifications(user_id: str, page: int = 1, per_page: int = 10):
        try:
            if not user_id:
                return Response(status=False, msg='Invalid user id', status_code=400)

            user_id = ObjectId(user_id)

            notifications = mongo.db[NOTIFICATIONS_COLLECTION].aggregate([
                {
                    '$match': {
                        '$expr': {
                            '$eq': ['$user_id', user_id]
                        }
                    },
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
                        'from': USERS_COLLECTION,
                        'as': 'users',
                        'localField': 'other_user_id',
                        'foreignField': '_id'
                    }
                },
                {
                    '$lookup': {
                        'from': RECIPES_COLLECTION,
                        'as': 'recipes',
                        'localField': 'recipe_id',
                        'foreignField': '_id'
                    }
                },
                {
                    '$lookup': {
                        'from': COMMENTS_COLLECTION,
                        'as': 'comments',
                        'localField': 'comment_id',
                        'foreignField': '_id'
                    }
                },
                {
                    '$lookup': {
                        'from': REPLIES_COLLECTION,
                        'as': 'replies',
                        'localField': 'reply_id',
                        'foreignField': '_id'
                    }
                },
                {
                    '$project': {
                        'created_at': 1,
                        'type': 1,
                        'other_user': {
                            '$arrayElemAt': ['$users', 0]
                        },
                        'recipe': {
                            '$cond': [{'$anyElementTrue': ['$recipes']}, {'$arrayElemAt': ['$recipes', 0]}, None]
                        },
                        'comment': {
                            '$cond': [{'$anyElementTrue': ['$comments']}, {'$arrayElemAt': ['$comments', 0]}, None]
                        },
                        'reply': {
                            '$cond': [{'$anyElementTrue': ['$replies']}, {'$arrayElemAt': ['$replies', 0]}, None]
                        }
                    }
                },
                {
                    '$project': {
                        'other_user._id': 1,
                        'other_user.email': 1,
                        'other_user.display_name': 1,
                        'other_user.image': 1,
                        'created_at': 1,
                        'type': 1,
                        'recipe.title': 1,
                        'recipe._id': 1,
                        'comment._id': 1,
                        'comment.body': 1,
                        'reply._id': 1,
                        'reply.comment_id': 1,
                        'reply.body': 1
                    }
                }
            ])

            return notifications
        except Exception as e:
            print(e)

    @staticmethod
    def update_user(edit_profile_request: EditProfileRequest, image: FileStorage = None):
        try:
            filter = {'_id': ObjectId(edit_profile_request.user_id)}
            user = mongo.db[USERS_COLLECTION].find_one_or_404(filter=filter)

            image_path = user['image']
            # Check if user uploaded image. If so, update image.
            if image:
                # Check if user has old image. If so, remove it.
                if user['image']:
                    old_image = os.path.join(
                        current_app.config['UPLOAD_FOLDER'], 'users', edit_profile_request.user_id, user['image'])
                    if os.path.exists(old_image):
                        os.remove(old_image)

                # Save the new uploaded file path
                image_path = upload_file(current_app.config['UPLOAD_FOLDER'], upload_type='users',
                                         _id=edit_profile_request.user_id, file=edit_profile_request.image)

            update_dict = {
                '$set': {
                    'display_name': edit_profile_request.display_name,
                    'email': edit_profile_request.email,
                    'image': image_path
                }
            }
            mongo.db[USERS_COLLECTION].find_one_and_update(
                filter=filter, update=update_dict)
            return Response(status=True, msg='Profile updated successfully', status_code=200, image=image_path)

        except NotFound:
            return Response(status=False, msg='User not found', status_code=404)
        except Exception as e:
            print(e)
            return Response(status=False, msg='Something went wrong', status_code=400)

    @staticmethod
    def update_firebase_token(payload):
        try:
            if 'firebase_token' not in payload or not payload['firebase_token']:
                return Response(status=False, msg='Invalid token', status_code=400)

            if 'user_id' not in payload or not payload['user_id']:
                return Response(status=False, msg='Invalid user id', status_code=400)

            user = mongo.db[USERS_COLLECTION].find_one_and_update(filter={'_id': ObjectId(payload['user_id'])}, update={'$set': {'firebase_token': payload['firebase_token']}}, return_document=ReturnDocument.AFTER, upsert=True)

            if not user:
                return Response(status=False, msg='No user found', status_code=404)
            
            return Response(status=True, msg='Token updated', status_code=200)
        except:           
            return Response(status=False, msg='Something went wrong', status_code=400)
