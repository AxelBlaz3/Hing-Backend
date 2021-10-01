from bson.objectid import ObjectId
import pymongo
from models.response import Response
from typing import Union
from repository import mongo
from constants import COMMENTS_COLLECTION, RECIPES_COLLECTION


class FeedRepository:

    @staticmethod
    def get_feed(user_id, category, page=1, per_page=10) -> Union[Response, dict]:
        try:
            user_id = ObjectId(user_id)
            pipeline = []
            if category and category != 0:
                pipeline.append({
                    '$match': {
                        'category': category
                    }
                })
            pipeline.extend([
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
                    '$project': {
                        'user.password': 0,
                        'likes': 0
                    }
                }])
            recipes = mongo.db[RECIPES_COLLECTION].aggregate(pipeline=pipeline)
            return recipes
        except Exception as e:
            print(e)
            return []
