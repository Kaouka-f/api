import os
import flask
from logger import logger
from redisIface import RedisIface
from helper.media import FILE_PATH
from helper.jwt import token_required

@token_required
def postPPSetting(id, scale, offsetX, offsetY):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy postPPSetting id error")
            return {}
        redis.redis_hset(f"user:{id}", 'scale', scale)
        redis.redis_hset(f"user:{id}", 'offsetX', offsetX)
        redis.redis_hset(f"user:{id}", 'offsetY', offsetY)
        del redis
        return "false"
    except Exception as e:
        del redis
        logger.critical("proxy Error while working postPPSetting with Redis: " + str(e))
        return "true"

def postPPSettingEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        scale = request_json['scale']
        offsetX = request_json['offsetX']
        offsetY = request_json['offsetY']
        return postPPSetting(id, scale, offsetX, offsetY)
    except Exception as e:
        logger.critical("proxy postPPSettingEntry args error: " + str(e))
        return 'true'