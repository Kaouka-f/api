import json
import flask
from redis.exceptions import RedisError
from logger import logger
from utils import sendNotif
from redisIface import RedisIface

def deleteInterressed(id, reqId):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy deleteInterressed id error")
            return {}
        reqOI_json_array = redis.redis_hget(id, 'requestsOfInterressed')
        reqOI_list = []
        if reqOI_json_array != None and reqOI_json_array != "":
            reqOI_list = json.loads(reqOI_json_array)
            if reqId in reqOI_list:
                reqOI_list.remove(reqId)
        updated_reqOI_json_array = json.dumps(reqOI_list)
        redis.redis_hset(id, "requestsOfInterressed", updated_reqOI_json_array)
        del redis
        return {}
    except RedisError as e:
        del redis
        print(f"Error while working with Redis deleteInterressed: {e}")
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy deleteInterressed error: " + str(e))

def deleteInterressedEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        reqId = request_json['reqId']
        return deleteInterressed(id, reqId)
    except Exception as e:
        logger.critical("proxy deleteInterressedEntry args error: " + str(e))
        return {}