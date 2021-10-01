from typing import Union
import pymongo
from pymongo.collection import ReturnDocument
from pymongo.results import InsertOneResult
from models.comment_like_request import CommentLikeRequest, ReplyLikeRequest
from models.comment_request import CommentRequest
from models.response import Response
from models.reply_request import ReplyRequest
from bson.objectid import ObjectId
from repository import mongo
from constants import COMMENTS_COLLECTION, RECIPES_COLLECTION, REPLIES_COLLECTION
from datetime import datetime


class CommentsRepository:

    @staticmethod
    def get_comments(user_id, recipe_id, page=1, per_page=10):
        try:
            comments = mongo.db[COMMENTS_COLLECTION].aggregate([
                {
                    '$match': {
                        'recipe_id': ObjectId(recipe_id)
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
                    '$addFields': {
                        'is_liked': {
                            '$in': [ObjectId(user_id), '$likes']
                        }
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
                        'from': REPLIES_COLLECTION,
                        'localField': '_id',
                        'foreignField': 'comment_id',
                        'as': 'replies'
                    }
                },
                {
                    '$project': {
                        'user': {
                            '$arrayElemAt': ['$user', 0]
                        },
                        'body': 1,
                        'created_at': 1,
                        'likes_count': {
                            '$size': '$likes'
                        },
                        'replies_count': {
                            '$size': '$replies'
                        },
                        'recipe_id': 1,
                        'is_liked': 1
                    }
                },
                {
                    '$project': {
                        'replies': 0,
                        'user.followers': 0,
                        'user.password': 0,
                        'user.email': 0,
                        'user.favorites': 0,
                        'user.likes': 0,
                        'user.following': 0
                    }
                }
            ])

            return comments
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def get_replies(user_id, comment_id, page=1, per_page=10):
        try:
            comments = mongo.db[REPLIES_COLLECTION].aggregate([
                {
                    '$match': {
                        'comment_id': ObjectId(comment_id)
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
                    '$addFields': {
                        'is_liked': {
                            '$in': [ObjectId(user_id), '$likes']
                        }
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
                        'from': REPLIES_COLLECTION,
                        'localField': '_id',
                        'foreignField': 'comment_id',
                        'as': 'replies'
                    }
                },
                {
                    '$project': {
                        'user': {
                            '$arrayElemAt': ['$user', 0]
                        },
                        'body': 1,
                        'created_at': 1,
                        'likes_count': {
                            '$size': '$likes'
                        },
                        'replies_count': {
                            '$size': '$replies'
                        },
                        'recipe_id': 1,
                        'is_liked': 1,
                        'comment_id': 1
                    }
                },
                {
                    '$project': {
                        'replies': 0,
                        'user.followers': 0,
                        'user.password': 0,
                        'user.email': 0,
                        'user.favorites': 0,
                        'user.likes': 0,
                        'user.following': 0
                    }
                }
            ])

            return comments
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def new_comment(comment_request: CommentRequest) -> Union[Response, dict]:
        try:
            user_id = ObjectId(comment_request.user_id)
            recipe_id = ObjectId(comment_request.recipe_id)
            comment_dict = comment_request.dict()
            comment_dict['user_id'] = user_id
            comment_dict['recipe_id'] = recipe_id
            comment_dict['created_at'] = datetime.utcnow()

            del comment_dict['is_reply']

            insert_result: InsertOneResult

            insert_result = mongo.db[COMMENTS_COLLECTION].insert_one(
                comment_dict)

            comment = mongo.db[COMMENTS_COLLECTION].aggregate([
                {
                    '$match': {
                        '_id': insert_result.inserted_id
                    }
                },
                {
                    '$addFields': {
                        'is_liked': {
                            '$in': [user_id, '$likes']
                        }
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
                        'from': REPLIES_COLLECTION,
                        'localField': '_id',
                        'foreignField': 'comment_id',
                        'as': 'replies'
                    }
                },
                {
                    '$project': {
                        'user': {
                            '$arrayElemAt': ['$user', 0]
                        },
                        'body': 1,
                        'created_at': 1,
                        'likes_count': {
                            '$size': '$likes'
                        },
                        'replies_count': {
                            '$size': '$replies'
                        },
                        'recipe_id': 1,
                        'is_liked': 1
                    }
                },
                {
                    '$project': {
                        'replies': 0,
                        'user.followers': 0,
                        'user.password': 0,
                        'user.email': 0,
                        'user.favorites': 0,
                        'user.likes': 0,
                        'user.following': 0
                    }
                },
            ])
            return comment
        except Exception as e:
            print(e)

    @staticmethod
    def new_reply(reply_request: ReplyRequest) -> Response:
        try:
            user_id = ObjectId(reply_request.user_id)
            comment_dict = reply_request.dict()
            comment_dict['user_id'] = user_id
            comment_dict['recipe_id'] = ObjectId(reply_request.recipe_id)
            comment_dict['comment_id'] = ObjectId(reply_request.comment_id)
            comment_dict['created_at'] = datetime.utcnow()
            del comment_dict['is_reply']

            insert_result: InsertOneResult = mongo.db[REPLIES_COLLECTION].insert_one(
                comment_dict)

            # if reply_request.is_reply:
            #     mongo.db[REPLIES_COLLECTION].find_one_and_update(
            #         filter={'_id': comment_dict['comment_id']}, update={'$inc': {'replies_count': 1}})
            # else:
            #     mongo.db[COMMENTS_COLLECTION].find_one_and_update(
            #         filter={'_id': comment_dict['comment_id']}, update={'$inc': {'replies_count': 1}})
            reply = mongo.db[REPLIES_COLLECTION].aggregate([
                {
                    '$match': {
                        '_id': insert_result.inserted_id
                    }
                },
                {
                    '$addFields': {
                        'is_liked': {
                            '$in': [user_id, '$likes']
                        }
                    }
                },
                {
                    '$lookup': {
                        'from': 'users',
                        'localField': 'user_id',
                        'foreignField': '_id',
                        'as': 'user'
                    }},
                {
                    '$project': {
                        'user': {
                            '$arrayElemAt': ['$user', 0]
                        },
                        'body': 1,
                        'created_at': 1,
                        'likes_count': 1,
                        'replies_count': 1,
                        'recipe_id': 1,
                        'is_liked': 1,
                        'comment_id': 1
                    }
                },
                {
                    '$project': {
                        'user.followers': 0,
                        'user.password': 0,
                        'user.email': 0,
                        'user.favorites': 0,
                        'user.likes': 0,
                        'user.following': 0
                    }
                },
            ])
            return reply
        except Exception as e:
            print(e)

    @staticmethod
    def like_comment(like_request: CommentLikeRequest) -> Response:
        try:
            comment_id = ObjectId(like_request.comment_id)
            user_id = ObjectId(like_request.user_id)
            filter = {'_id': comment_id}

            mongo.db[COMMENTS_COLLECTION].find_one(filter, {'_id': 1})
            comment = mongo.db[COMMENTS_COLLECTION].find_one(
                {'_id': comment_id, 'likes': user_id}, {'_id': 1})

            if comment is None:
                update = {
                    '$addToSet': {
                        'likes': user_id
                    },
                    '$inc': {
                        'likes_count': 1
                    }
                }
                updated_comment = mongo.db[COMMENTS_COLLECTION].find_one_and_update(
                    filter=filter, update=update, return_document=ReturnDocument.AFTER)

                if not updated_comment:
                    return Response(status=False, msg='Comment not found', status_code=404)

            return Response(status=True, msg='Likes updated', status_code=200)
        except Exception as e:
            print(e)

    @staticmethod
    def like_reply(like_request: ReplyLikeRequest) -> Response:
        try:
            reply_id = ObjectId(like_request.reply_id)
            user_id = ObjectId(like_request.user_id)
            filter = {'_id': ObjectId(like_request.reply_id)}

            mongo.db[REPLIES_COLLECTION].find_one(filter, {'_id': 1})
            reply = mongo.db[REPLIES_COLLECTION].find_one(
                {'_id': reply_id, 'likes': user_id})

            if not reply:
                update = {
                    '$addToSet': {
                        'likes': ObjectId(like_request.user_id)
                    },
                    '$inc': {
                        'likes_count': 1
                    }
                }
                updated_reply = mongo.db[REPLIES_COLLECTION].find_one_and_update(
                    filter=filter, update=update, return_document=ReturnDocument.AFTER)

                if not updated_reply:
                    return Response(status=False, msg='Comment not found', status_code=404)

            return Response(status=True, msg='Likes updated', status_code=200)
        except Exception as e:
            print(e)

    @staticmethod
    def unlike_comment(like_request: CommentLikeRequest) -> Response:
        try:
            comment_id = ObjectId(like_request.comment_id)
            user_id = ObjectId(like_request.user_id)

            filter = {'_id': comment_id}

            mongo.db[COMMENTS_COLLECTION].find_one(filter, {'_id': 1})
            comment = mongo.db[COMMENTS_COLLECTION].find_one(
                {'_id': comment_id, 'likes': user_id}, {'_id': 1})

            if comment:
                update = {
                    '$pull': {
                        'likes': ObjectId(like_request.user_id)
                    },
                    '$inc': {
                        'likes_count': -1
                    }
                }
                updated_comment = mongo.db[COMMENTS_COLLECTION].find_one_and_update(
                    filter=filter, update=update, return_document=ReturnDocument.AFTER)

                if not updated_comment:
                    return Response(status=False, msg='Comment not found', status_code=404)

            return Response(status=True, msg='Likes updated', status_code=200)
        except Exception as e:
            print(e)

    @staticmethod
    def unlike_reply(like_request: ReplyLikeRequest) -> Response:
        try:
            reply_id = ObjectId(like_request.reply_id)
            user_id = ObjectId(like_request.user_id)
            filter = {'_id': reply_id}

            mongo.db[REPLIES_COLLECTION].find_one(filter, {'_id': 1})
            reply = mongo.db[REPLIES_COLLECTION].find_one(
                {'_id': reply_id, 'likes': user_id})

            if reply:
                update = {
                    '$pull': {
                        'likes': user_id
                    },
                    '$inc': {
                        'likes_count': -1
                    }
                }
                updated_reply = mongo.db[REPLIES_COLLECTION].find_one_and_update(
                    filter=filter, update=update, return_document=ReturnDocument.AFTER)

                if not updated_reply:
                    return Response(status=False, msg='Comment not found', status_code=404)

            return Response(status=True, msg='Likes updated', status_code=200)
        except Exception as e:
            print(e)
