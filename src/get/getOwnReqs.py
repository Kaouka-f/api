import json
import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface
from helper.jwt import token_required

@token_required
def getOwnReqs(id, lastReqId):
    redis = RedisIface()
    size = 40960
    try:
        json_object = {}
        member_num = 0
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy getOwnReqs id error")
            return {}
        req_result = redis.redis_hget(id, 'requests')
        if req_result == None or req_result == "":
            del redis
            return {}
        requests_list = json.loads(req_result)
        startIndex = 0
        if lastReqId and lastReqId != '':
            startIndex = requests_list.index(lastReqId) + 1
        for req in requests_list[startIndex:]:
            request = redis.redis_hgetall(req)
            if request:
                if (len(str(json_object).encode('utf-8')) + len(str(request).encode('utf-8'))) < size:
                    json_object[member_num] = request
                    member_num+=1
                else:
                    break
        del redis
        return json_object
        # TODO: need authentication
    except RedisError as e:
        del redis
        print(f"Error while working with Redis: {e}")
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy get own reqs error: " + str(e))
        return {}

def getOwnReqsEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        lastReqId = request.args.get('lastReqId')
        return getOwnReqs(id, lastReqId)
    except Exception as e:
        logger.critical("proxy getOwnReqsEntry args error: " + str(e))
        return {}