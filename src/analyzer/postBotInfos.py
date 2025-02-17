import json
import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

def postBotInfos(id, lng, lat, name, imgUrl, scale, offsetX, offsetY, socketId, password):
    redis = RedisIface()
    try:
        if(password == 'zigzag'):
            redis.redis_hset(id, 'lng', lng)
            redis.redis_hset(id, 'lat', lat)
            redis.redis_hset(id, 'name', name)
            redis.redis_hset(id, 'img', imgUrl)
            redis.redis.hset(id, 'scale', scale)
            redis.redis.hset(id, 'offsetX', offsetX)
            redis.redis.hset(id, 'offsetY', offsetY)
            redis.redis_hset(id, 'socketId', socketId)
            # redis.redis_hset(id, 'notifToken', notifToken)
            del redis
            return {}
        del redis
        return {}
    except RedisError as e:
        del redis
        print(f"Error while working with Redis: {e}")
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy postBotInfos error: " + str(e))
        return {}

def postBotInfosEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        lng = request_json['lng']
        lat = request_json['lat']
        name = request_json['name']
        imgUrl = request_json['img']
        scale = request_json['scale']
        offsetX = request_json['offsetX']
        offsetY = request_json['offsetY']
        socketId = request_json['socketId']
        # notifToken = request_json['notifToken']
        password = request_json['password']
        return postBotInfos(id, lng, lat, name, imgUrl, scale, offsetX, offsetY, socketId, password)
    except Exception as e:
        logger.critical("proxy postBotInfosEntry args error: " + str(e))
        return {}