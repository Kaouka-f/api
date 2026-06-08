import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface


def getLikes(reqId):
    redis = RedisIface()
    try:
        likes = redis.redis_hget(reqId, "likes")
        del redis
        return {'likes': likes}
    except RedisError as e:
        print(f"Error while working with Redis: {e}")
        return {}
    except Exception as e:
        logger.critical("proxy getLikes error: " + str(e))
        return {}


def getLikesEntry():
    try:
        request = flask.request
        reqId = request.args.get('reqId')
        return getLikes(reqId)
    except Exception as e:
        logger.critical("proxy getLikesEntry args error: " + str(e))
        return {}
