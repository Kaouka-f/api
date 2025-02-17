import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

def hashGetAll(password, hash):
    try:
        redis = RedisIface()
        response = {}
        # TODO: create JWT for bot creation
        if password == 'zigzag':
            response = redis.redis_hgetall(hash)
        del redis
        return response
    except RedisError as e:
        logger.critical("proxy hashGetAll error redis: " + str(e))
        del redis
        return {}

def hashGetAllEntry():
    try:
        request = flask.request
        password = request.args.get('password')
        hash = request.args.get('hash')
        return hashGetAll(password, hash)
    except Exception as e:
        logger.critical("proxy hashGetAllEntry args error: " + str(e))
        return {}