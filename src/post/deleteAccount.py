import utils
import flask
from redis.exceptions import RedisError
from logger import logger
from redisIface import RedisIface
from post.deleteReq import deleteReqStatic
from get.getAllReqs import getAllReqs

def deleteAccountStatic(redis, id):
    try:
        # delete push notif token
        # token = redis.redis_hget(id, 'notifToken')
        # utils.delete_fcm_instance(token)
        # delete all requests
        requests = redis.redis_hget(id, 'requests')
        for reqId in requests:
            deleteReqStatic(redis, reqId)
        # delete all redis infos
        redis.redis_deleteall(id)
        return ''
    except RedisError as e:
        logger.critical("proxy deleteAccount error redis: " + str(e))
        return {}
    except Exception as e:
        logger.critical("proxy deleteAccount args error: " + str(e))

def deleteAccount(id):
    redis = RedisIface()
    try:
        # Check if id is valid
        id = redis.check_id(id)
        if id == None:
            del redis
            logger.critical("proxy deleteAccount id error")
            return {}
        res = deleteAccountStatic(redis, id)
        del redis
        return res
    except RedisError as e:
        del redis
        logger.critical("proxy deleteAccount error redis: " + str(e))
        return {}

def deleteAccountEntry():
    try:
        # arg check
        request = flask.request
        request_json = request.get_json()
        return deleteAccount(request_json['id'])
    except Exception as e:
        logger.critical("proxy deleteAccountEntry args error: " + str(e))
        return {}