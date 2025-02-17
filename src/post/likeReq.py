import json
import flask
from redis.exceptions import RedisError
from logger import logger
from utils import sendNotif
from redisIface import RedisIface

def likeReq(id, reqId):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy likeReq id error")
            return {}
        if redis.redis.hexists(reqId, "likeNb") == 0:
            redis.redis_hset(reqId, "likeNb", "0")
        if redis.redis.hexists(reqId, "likes") == 0:
            redis.redis_hset(reqId, "likes", "[]")
        likesJson = redis.redis_hget(reqId, "likes")
        likesNb = redis.redis_hget(reqId, "likeNb")
        likes = json.loads(likesJson)
        # send notif to reqId
        targetid = redis.redis_hget(reqId, "id")
        notifToken = redis.redis_hget(targetid, "notifToken")
        pseudo = redis.redis_hget(id, "name")
        if id not in likes:
            likes.append(id)
            likesNb = int(likesNb) + 1
            sendNotif(notifToken, pseudo, "à aimé ton post")
            # add in req of interressed
            reqOI_json_array = redis.redis_hget(id, 'requestsOfInterressed')
            reqOI_list = []
            if reqOI_json_array != None and reqOI_json_array != "":
                reqOI_list = json.loads(reqOI_json_array)
                reqOI_list.append(reqId)
            else:
                reqOI_list = []
                reqOI_list.append(reqId)
            updated_reqOI_json_array = json.dumps(reqOI_list)
            redis.redis_hset(id, "requestsOfInterressed", updated_reqOI_json_array)
        else:
            likes.remove(id)
            likesNb = int(likesNb) - 1
            sendNotif(notifToken, pseudo, "n'aime plus ton post")
            # delete in req of interressed
            reqOI_json_array = redis.redis_hget(id, 'requestsOfInterressed')
            reqOI_list = []
            if reqOI_json_array != None and reqOI_json_array != "":
                reqOI_list = json.loads(reqOI_json_array)
                if reqId in reqOI_list:
                    reqOI_list.remove(reqId)
            updated_reqOI_json_array = json.dumps(reqOI_list)
            redis.redis_hset(id, "requestsOfInterressed", updated_reqOI_json_array)
        newLikes = json.dumps(likes)
        redis.redis_hset(reqId, "likeNb", str(likesNb))
        redis.redis_hset(reqId, "likes", newLikes)
        del redis
        return {}
    except RedisError as e:
        del redis
        print(f"Error while working with Redis likeReq: {e}")
        return {}
    except Exception as e:
        del redis
        logger.critical("proxy likeReq error: " + str(e))

def likeReqEntry():
    try:
        request = flask.request
        request_json = request.get_json()
        id = request_json['id']
        reqId = request_json['reqId']
        return likeReq(id, reqId)
    except Exception as e:
        logger.critical("proxy likeReqEntry args error: " + str(e))
        return {}