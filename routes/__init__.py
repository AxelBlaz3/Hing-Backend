from flask import Blueprint

user_api = Blueprint('user_api', __name__)
recipe_api = Blueprint('recipe_api', __name__)
feed_api = Blueprint('feed_api', __name__)
comments_api = Blueprint('comments_api', __name__)