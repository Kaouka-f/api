import json
import flask
from logger import logger
from redisIface import RedisIface

def postName(id, name):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy postName id error")
            return {}
        redis.redis_hset(f"user:{id}", 'name', name)
        del redis
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy Error while working postName with Redis: " + str(e))
        return {}

def postNameEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        name = request_json['name']
        return postName(id, name)
    except Exception as e:
        logger.critical("proxy postNameEntry args error: " + str(e))
        return {}