import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

def getBots(password):
    try:
        redis = RedisIface()
        response = {}
        # TODO: create JWT for bot creation
        if password == 'zigzag':
            response = redis.redis.lrange('bots', 0, -1)
            response_data = [data.decode('utf-8') for data in response]
        del redis
        return response_data
    except RedisError as e:
        logger.critical("proxy getBots error redis: " + str(e))
        del redis
        return {}

def getBotsEntry():
    try:
        request = flask.request
        password = request.args.get('password')
        return getBots(password)
    except Exception as e:
        logger.critical("proxy getBotsEntry args error: " + str(e))
        return {}