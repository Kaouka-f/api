import json
import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface
from helper.jwt import token_required

@token_required
def isBlocked(id, userId):
    redis = RedisIface()
    size = 40960
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy isBlocked id error")
            return {}
        req_result = redis.redis_hget(id, 'blockedUser')
        if req_result == None or req_result == "":
            del redis
            return {}
        requests_list = json.loads(req_result)
        del redis
        if userId in requests_list:
            return {'result':'true'}
        else:
            return {'result':'false'}
        # TODO: need authentication
    except RedisError as e:
        del redis
        print(f"Error while working with Redis: {e}")
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy get blocked error: " + str(e))
        return {}

def isBlockedEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        userId = request.args.get('userId')
        return isBlocked(id, userId)
    except Exception as e:
        logger.critical("proxy isBlockedEntry args error: " + str(e))
        return {}