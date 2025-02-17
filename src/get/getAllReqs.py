import json
import flask
from logger import logger
from redisIface import RedisIface

def getAllReqs(id, lastReqId):
    size = 40960
    try:
        redis = RedisIface()
        requests_json_array = redis.redis_hget(id, 'requests')
        requests = json.loads(requests_json_array)
        json_object = {}
        member_num = 0
        startIndex = 0
        if lastReqId and lastReqId != '':
            startIndex = requests.index(lastReqId)
        for req in requests[startIndex:]:
            tmpReq = {}
            request = redis.redis_hgetall(req)
            tmpReq['likeNb'] = request['likeNb'] if 'likeNb' in request else "0"
            tmpReq['signalNb'] = request['signalNb'] if 'signalNb' in request else "0"
            tmpReq['reqId'] = request['reqId'] if 'reqId' in request else ""
            tmpReq['reqTime'] = request['reqTime'] if 'reqTime' in request else ""
            tmpReq['text'] = request['text'] if 'text' in request else ""
            tmpReq['media'] = request['media'] if 'media' in request else ""
            if (len(str(json_object).encode('utf-8')) + len(str(tmpReq).encode('utf-8'))) < size:
                json_object[member_num] = tmpReq
                member_num+=1
        del redis
        return json_object
    except Exception as e:
            logger.critical('proxy getAllReqs error: ' + str(e))
            del redis
            return {}

def getAllReqsEntry():
    try:
        request = flask.request
        id = request.args.get('id')
        lastReqId = request.args.get('lastReqId')
        return getAllReqs(id, lastReqId)
    except Exception as e:
        logger.critical("proxy getAllReqsEntry args error: " + str(e))
        return {}