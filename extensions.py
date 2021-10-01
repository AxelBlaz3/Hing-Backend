from enum import IntEnum

class MediaType(IntEnum):
    IMAGE = 1
    VIDEO = 2

class NotificationType(IntEnum):
    NEW_FOLLOWER = 0
    NEW_POST = 1
    NEW_COMMENT = 2
    NEW_REPLY = 3
    LIKE_POST = 4
    LIKE_COMMENT = 5
    LIKE_REPLY = 6