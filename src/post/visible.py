import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface
from helper.jwt import token_required

@token_required
def visible(id, value):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy visible id error")
            return {}
        if value == 'true':
            redis.redis_hset(id, 'visible', "1")
        elif value == 'false':
            redis.redis_hset(id, 'visible', "0")
        else:
            del redis
            return "true"
        del redis
        return "false"
    except RedisError as e:
        print(f"Error while working with Redis: {e}")
        return "true"
    except Exception as e:
        logger.critical("proxy get arrounds args error: " + str(e))

def visibleEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        value = request_json['value']
        return visible(id, value)
    except Exception as e:
        logger.critical("proxy visibleEntry args error: " + str(e))
        return {}