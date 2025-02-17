import json
import flask
from logger import logger
from redisIface import RedisIface

def postNotifToken(id, notifToken):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy postNotifToken id error")
            return {}
        redis.redis_hset(id, 'notifToken', notifToken)
        del redis
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy Error while working postNotifToken with Redis: " + str(e))
        return {}

def postNotifTokenEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        notifToken = request_json['notifToken']
        return postNotifToken(id, notifToken)
    except Exception as e:
        logger.critical("proxy postNotifTokenEntry args error: " + str(e))
        return {}