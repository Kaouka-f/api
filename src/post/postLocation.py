import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

from helper.jwt import token_required

@token_required
def postLocation(id, long, lat):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id is None:
            del redis
            logger.critical("proxy post location id error")
            return {}
        redis.redis_geoadd(long, lat, id)
        del redis
        return {}
    except RedisError as e:
        logger.critical("proxy post location error redis: " + str(e))
        return {}
    except Exception as e:
        logger.critical("proxy post location args error: " + str(e))


def postLocationEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        long = request_json['long']
        lat = request_json['lat']
        return postLocation(id, long, lat)
    except Exception as e:
        logger.critical("proxy post location args error: " + str(e))
        return {}
