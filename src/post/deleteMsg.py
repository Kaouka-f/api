import json
import os
from urllib.parse import urlparse
import flask
from logger import logger
from redisIface import RedisIface
from helper.media import FILE_PATH

from helper.jwt import token_required

@token_required
def deleteMsg(id, media):
    try:
        redis = RedisIface()
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy deleteMsg id error")
            return {}
        if media:
            parsed_url = urlparse(media)
            new_path = parsed_url.path.replace("/proxy/stream", "")
            if id in new_path:
                if os.path.exists(FILE_PATH + new_path):
                    os.remove(FILE_PATH + new_path)
                    return {'result':"true"}
        del redis
        return {'result':"false"}
    except Exception as e:
        del redis
        logger.critical("proxy deleteMsg args error: " + str(e))
        return {'result':"false"}

def deleteMsgEntry():
    try:
        request = flask.request
        req_json = request.get_json()
        id = req_json['id']
        media = req_json['media']
        return deleteMsg(id, media)
    except Exception as e:
        logger.critical("proxy deleteMsgEntry args error: " + str(e))
        return {}