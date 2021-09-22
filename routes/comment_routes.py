from models.reply_request import ReplyRequest
from models.comment_like_request import CommentLikeRequest, ReplyLikeRequest
from bson import json_util
from flask import json
from flask.json import jsonify
from models.response import Response
from pydantic.error_wrappers import ValidationError
from routes import comments_api
from constants import COMMENT_UNLIKE_ENDPOINT, COMMENT_LIKE_ENDPOINT, GET_COMMENTS, GET_REPLIES, NEW_COMMENT_ENDPOINT, NEW_REPLY_ENDPOINT, REPLY_LIKE_ENDPOINT, REPLY_UNLIKE_ENDPOINT
from repository.comments_repository import CommentsRepository
from models.comment_request import CommentRequest
from flask import request
from pymongo.command_cursor import CommandCursor


@comments_api.get(GET_COMMENTS)
def get_comments(recipe_id):
    user_id = request.args.get(key='user_id', default=None)
    page = request.args.get(key='page', default=1, type=int)
    per_page = request.args.get(key='per_page', default=10, type=int)

    comments = CommentsRepository.get_comments(
        recipe_id=recipe_id, user_id=user_id, page=page, per_page=per_page)
    return jsonify(json.loads(json_util.dumps(comments)))


@comments_api.get(GET_REPLIES)
def get_replies(comment_id):
    user_id = request.args.get(key='user_id', default=None)
    page = request.args.get(key='page', default=1, type=int)
    per_page = request.args.get(key='per_page', default=10, type=int)

    comments = CommentsRepository.get_replies(
        comment_id=comment_id, user_id=user_id, page=page, per_page=per_page)
    return jsonify(json.loads(json_util.dumps(comments)))


@comments_api.post(NEW_COMMENT_ENDPOINT)
def new_comment():
    try:
        comment_request = CommentRequest(**request.json)

        result = CommentsRepository.new_comment(
            comment_request=comment_request)
        if isinstance(result, CommandCursor):
            return jsonify(json.loads(json_util.dumps(result))[0]), 201

        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@comments_api.put(COMMENT_LIKE_ENDPOINT)
def like_comment():
    try:
        like_request = CommentLikeRequest(**request.json)

        result = CommentsRepository.like_comment(like_request=like_request)
        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@comments_api.put(COMMENT_UNLIKE_ENDPOINT)
def unlike_comment():
    try:
        like_request = CommentLikeRequest(**request.json)

        result = CommentsRepository.unlike_comment(like_request=like_request)
        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@comments_api.post(NEW_REPLY_ENDPOINT)
def new_reply():
    try:
        reply_request = ReplyRequest(**request.json)

        result = CommentsRepository.new_reply(reply_request=reply_request)
        if isinstance(result, CommandCursor):
            return jsonify(json.loads(json_util.dumps(result))[0]), 201

        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@comments_api.put(REPLY_LIKE_ENDPOINT)
def like_reply():
    try:
        like_request = ReplyLikeRequest(**request.json)

        result = CommentsRepository.like_reply(like_request=like_request)
        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400


@comments_api.put(REPLY_UNLIKE_ENDPOINT)
def unlike_reply():
    try:
        like_request = ReplyLikeRequest(**request.json)

        result = CommentsRepository.unlike_reply(like_request=like_request)
        return result.dict(), result.status_code
    except ValidationError as e:
        return e.json(), 400
    except Exception as e:
        print(e)
        return Response(status=False, msg='Some error occured', status_code=400).dict(), 400
