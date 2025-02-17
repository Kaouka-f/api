import json
import flask
from logger import logger
from redisIface import RedisIface
from redis.exceptions import RedisError

def blockUser(id, userId):
    redis = RedisIface()
    # Check if id is valid
    id = redis.check_id(id)
    if id == None:
        del redis
        logger.critical("proxy blockUser id error")
        return {}
    try:
        blockedUser_json = redis.redis_hget(id, "blockedUser")
        blockedUser_list = []
        if blockedUser_json != None and blockedUser_json != "":
            blockedUser_list = json.loads(blockedUser_json)
            if userId in blockedUser_list:
                blockedUser_list.remove(userId)
            else:
                blockedUser_list.append(userId)
        updated_blockedUser_json_array = json.dumps(blockedUser_list)
        redis.redis_hset(id, "blockedUser", updated_blockedUser_json_array)
        del redis
        return {'result':'true'}
    except RedisError as e:
        del redis
        print(f"Error while working with Redis: {e}")
        return {}
    except Exception as e:
        del redis
        print(f"Error in blockUser : {e}")
        return {}

def blockUserEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        userId = request_json['userId']
        return blockUser(id, userId)
    except Exception as e:
        logger.critical("proxy blockUserEntry args error: " + str(e))
        return {}