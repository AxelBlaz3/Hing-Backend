from flask.json import jsonify
from routes import feed_api
from constants import FEED_ENDPOINT
from flask import request, jsonify, json
from bson import json_util
from repository.feed_repository import FeedRepository

@feed_api.get(FEED_ENDPOINT)
def get_feed(user_id):
    page = request.args.get(key='page', default=1, type=int)
    category = request.args.get(key='category', default=None, type=int)
    if not page:
        return jsonify(json.loads(json_util.dumps(FeedRepository.get_feed(user_id=user_id, category=category)))) 
    else:
        return jsonify(json.loads(json_util.dumps(FeedRepository.get_feed(user_id=user_id, category=category, page=page))))
        