import json
import flask
from logger import logger
from redisIface import RedisIface

def getRequest(reqid):
    try:
        redis = RedisIface()
        req = redis.redis_hgetall(reqid)
        if req:
            infos = redis.redis_hgetall(req['id'])
            req['name'] = infos['name'] if 'name' in infos else "undefined"
            req['picture'] = infos['img'] if 'img' in infos else "https://elaborium.site/proxy/stream/default/profile.jpg"
            req['scale'] = infos['scale'] if 'scale' in infos else "1"
            req['offsetX'] = infos['offsetX'] if 'offsetX' in infos else "0"
            req['offsetY'] = infos['offsetY'] if 'offsetY' in infos else "0"
            req['connected'] = infos['connected'] if 'connected' in infos else "false"
        del redis
        return req
    except Exception as e:
            logger.critical("proxy getRequest error: " + str(e))
            del redis
            return {}

def getRequestEntry():
    try:
        request = flask.request
        reqid = request.args.get('reqId')
        return getRequest(reqid)
    except Exception as e:
        logger.critical("proxy getRequestEntry args error: " + str(e))
        return {}