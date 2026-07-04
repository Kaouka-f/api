import json
import os
from urllib.parse import urlparse
import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

from helper.media import FILE_PATH


def deleteReqStatic(redis, reqId):
    try:
        # Delete all comments from requests
        requests_json_array = redis.redis_hget(reqId, 'comments')
        updated_comments = []

        def recursive_get_comment(comments):
            comments_list = json.loads(comments)
            for commentId in comments_list:
                updated_comments.append(commentId)
                if redis.redis.hexists(commentId, 'comments'):
                    commentId_json_array = redis.redis_hget(
                        commentId, 'comments')
                    recursive_get_comment(commentId_json_array)
        if requests_json_array is not None and requests_json_array != "":
            recursive_get_comment(requests_json_array)
            for commentId in updated_comments:
                # delete media
                media = redis.redis_hget(commentId, 'media')
                if media is not None and media != "":
                    medias_json = json.loads(media)
                    for media_json in medias_json:
                        parsed_url = urlparse(media_json)
                        path = parsed_url.path
                        if os.path.exists(FILE_PATH + path):
                            os.remove(FILE_PATH + path)
                redis.redis_deleteall(commentId)
        # Delete media from request
        media = redis.redis_hget(reqId, 'media')
        if media is not None and media != "":
            parsed_url = urlparse(media)
            path = parsed_url.path
            if os.path.exists(FILE_PATH + path):
                os.remove(FILE_PATH + path)
        # before delete comment, delete commentId and decrease commentNb from mother request
        # get father reqId
        attachReqId = ""
        if redis.redis.hexists(reqId, 'attachReqId'):
            attachReqId = redis.redis.hget(reqId, 'attachReqId')
            # decrease comment nb
            commentNb = redis.redis_hget(attachReqId, "commentNb")
            if commentNb is not None and commentNb != "":
                commentNb = int(commentNb)
            else:
                commentNb = 0
            commentNb -= 1
            redis.redis_hset(attachReqId, "commentNb", str(commentNb))
            # delete comment in request key
            comments_json_array = redis.redis_hget(attachReqId, 'comments')
            comments_list = []
            if comments_json_array is not None and comments_json_array != "":
                comments_list = json.loads(comments_json_array)
                if reqId in comments_list:
                    comments_list.remove(reqId)
            else:
                comments_list = []
            updated_json_array = json.dumps(comments_list)
            redis.redis_hset(attachReqId, "comments", updated_json_array)
        # There is no attachReqId so its not a comment, delete req from id
        else:
            # Delete reqId from requests list
            id = redis.redis_hget(reqId, 'id')
            request_json_array = redis.redis_hget(id, 'requests')
            requests_list = []
            if request_json_array is not None and request_json_array != "":
                requests_list = json.loads(request_json_array)
                if reqId in requests_list:
                    requests_list.remove(reqId)
            else:
                requests_list = []
            updated_json_array = json.dumps(requests_list)
            redis.redis_hset(id, "requests", updated_json_array)
        redis.redis.delete(reqId)
        return {}
    except RedisError as e:
        print(f"Error while working with Redis: {e}")
        logger.critical(
            "proxy Error in deleteReq while working with Redis deleteReq: " + str(e))
        return {}
    except Exception as e:
        logger.critical("proxy deleteReq args error: " + str(e))


def deleteReq(id, reqId):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id is None:
            del redis
            logger.critical("proxy deleteReq id error")
            return {}
        res = deleteReqStatic(redis, reqId)
        del redis
        return res
    except RedisError as e:
        print(f"Error while working with Redis: {e}")
        logger.critical(
            "proxy Error in deleteReq while working with Redis deleteReq: " + str(e))
        return {}


def deleteReqEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        reqId = request_json['reqId']
        return deleteReq(id, reqId)
    except Exception as e:
        logger.critical("proxy deleteReqEntry args error: " + str(e))
        return {}
