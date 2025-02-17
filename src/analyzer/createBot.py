import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface

def createBot(id, privateId, name, imgUrl, scale, offsetX, offsetY, socketId, lng, lat, password):
    redis = RedisIface()
    response = {}
    try:
        if(password == 'zigzag'):
            redis.redis_hset(id, 'name', name)
            redis.redis_hset(id, 'privateid', privateId)
            redis.redis_hset(id, 'img', imgUrl)
            redis.redis_hset(id, 'scale', str(scale))
            redis.redis_hset(id, 'offsetX', str(offsetX))
            redis.redis_hset(id, 'offsetY', str(offsetY))
            redis.redis_hset(id, 'lng', str(lng))
            redis.redis_hset(id, 'lat', str(lat))
            redis.redis_hset(id, 'socketId', socketId)
            redis.redis_hset(id, 'bot', 'true')
            redis.redis.rpush('bots', id+'_'+privateId)
            del redis
            return response
        del redis
    except RedisError as e:
        del redis
        logger.critical("proxy createBot error redis: " + str(e))
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy createBot other error: " + str(e))

def createBotEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        privateId = request_json['privateId']
        name = request_json['name']
        imgUrl = request_json['imgUrl']
        scale = request_json['scale']
        offsetX = request_json['offsetX']
        offsetY = request_json['offsetY']
        socketId = request_json['socketId']
        lng = request_json['lng']
        lat = request_json['lat']
        password = request_json['password']
        return createBot(id, privateId, name, imgUrl, scale, offsetX, offsetY, socketId, lng, lat, password)
    except Exception as e:
        logger.critical("proxy createBotEntry args error: " + str(e))
        return {}