# Mongo collection names
USERS_COLLECTION = 'users'
RECIPES_COLLECTION = 'recipes'
MEDIA_COLLECTION = 'media'
COMMENTS_COLLECTION = 'comments'
REPLIES_COLLECTION = 'replies'
NOTIFICATIONS_COLLECTION = 'notifications'
USER_INGREDIENTS_COLLECTION = 'user_ingredients'
REPORTED_RECIPES_COLLECTION = 'reported_recipes'
# BLOCKED_USER_COLLECTION= 'blocked_users'


# Endpoints
API_VERSION = 1
ENDPOINT_PREFIX = f'/api/v{API_VERSION}'

USER_ENDPOINT_PREFIX = 'user'
RECIPE_ENDPOINT_PREFIX = 'recipe'

# User endpoints
SIGNUP_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/signup'
LOGIN_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/login'
GET_FOLLOWERS_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/<user_id>/followers'
GET_FOLLOWING_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/<user_id>/following'
GET_USER_POSTS_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/<user_id>/posts'
GET_USER_FAVORITES_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/<user_id>/favorites'
FOLLOW_USER_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/follow'
UNFOLLOW_USER_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/unfollow'
GET_NOTIFICATIONS_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/<user_id>/notifications'
EDIT_PROFILE_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/update'
CREATE_NEW_PASSWORD_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/create/password'
SEND_RESET_CODE_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/send/resetcode'
UPDATE_FIREBASE_TOKEN_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/update/token'
UPDATE_MY_INGREDIENTS_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/update/ingredients'
# BLOCK_USER_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/block'
CHANGE_PASSWORD_ENDPOINT = f'{ENDPOINT_PREFIX}/{USER_ENDPOINT_PREFIX}/change/password'

# Recipe endpoints
NEW_RECIPE_ENDPOINT = f'{ENDPOINT_PREFIX}/{RECIPE_ENDPOINT_PREFIX}'
GET_RECIPE_ENDPOINT = f'{ENDPOINT_PREFIX}/{RECIPE_ENDPOINT_PREFIX}'
LIKE_RECIPE_ENDPOINT = f'{ENDPOINT_PREFIX}/{RECIPE_ENDPOINT_PREFIX}/like'
UNLIKE_RECIPE_ENDPOINT = f'{ENDPOINT_PREFIX}/{RECIPE_ENDPOINT_PREFIX}/unlike'
ADD_TO_FAVORITES_ENDPOINT = f'{ENDPOINT_PREFIX}/{RECIPE_ENDPOINT_PREFIX}/favorite'
REMOVE_FROM_FAVORITES_ENDPOINT = f'{ENDPOINT_PREFIX}/{RECIPE_ENDPOINT_PREFIX}/unfavorite'
GET_RECIPE_LIKES_ENDPOINT = f'{ENDPOINT_PREFIX}/{RECIPE_ENDPOINT_PREFIX}/<recipe_id>/likes'
SEARCH_RECIPES_ENDPOINT = f'{ENDPOINT_PREFIX}/{RECIPE_ENDPOINT_PREFIX}/search/<query>'
REPORT_RECIPE_ENDPOINT = f'{ENDPOINT_PREFIX}/{RECIPE_ENDPOINT_PREFIX}/report'


# Comment endpoints
GET_COMMENTS = f'{ENDPOINT_PREFIX}/comments/<recipe_id>'
GET_REPLIES = f'{ENDPOINT_PREFIX}/comments/replies/<comment_id>'
NEW_COMMENT_ENDPOINT = f'{ENDPOINT_PREFIX}/comment'
NEW_REPLY_ENDPOINT = f'{ENDPOINT_PREFIX}/comment/reply'
COMMENT_LIKE_ENDPOINT = f'{ENDPOINT_PREFIX}/comment/like'
REPLY_LIKE_ENDPOINT = f'{ENDPOINT_PREFIX}/comment/reply/like'
COMMENT_UNLIKE_ENDPOINT = f'{ENDPOINT_PREFIX}/comment/unlike'
REPLY_UNLIKE_ENDPOINT = f'{ENDPOINT_PREFIX}/comment/reply/unlike'

# Feed endpoints
FEED_ENDPOINT = f'{ENDPOINT_PREFIX}/feed/<user_id>'
