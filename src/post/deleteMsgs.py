import json
import os
from urllib.parse import urlparse
import flask
from logger import logger
from redisIface import RedisIface
from helper.media import FILE_PATH

from helper.jwt import token_required

@token_required
def deleteMsgs(id):
    try:
        redis = RedisIface()
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy deleteMsgs id error")
            return {}
        if redis.redis.hexists(id, 'msgs'):
            msg_list_json = redis.redis_hget(id, 'msgs')
            if msg_list_json:
                msg_list = json.loads(msg_list_json)
                for msg in msg_list:
                    redis.redis_deleteall("msg:"+msg)
                redis.redis_hset(id, 'msgs', json.dumps([]))
        del redis
        return ''
    except Exception as e:
        del redis
        logger.critical("proxy deleteMsgs args error: " + str(e))
        return {}

def deleteMsgsEntry():
    try:
        request = flask.request
        req_json = request.get_json()
        id = req_json['id']
        return deleteMsgs(id)
    except Exception as e:
        logger.critical("proxy deleteMsgsEntry args error: " + str(e))
        return {}